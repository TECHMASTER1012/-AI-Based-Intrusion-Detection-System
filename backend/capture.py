import sys
import os
import threading
from scapy.all import sniff, IP, TCP, UDP, ICMP
import time

# Add root project dir to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.model_predict import predict_packet
from backend.database import insert_log

class PacketCapture:
    def __init__(self):
        self.is_capturing = False
        self.thread = None

    def _packet_callback(self, packet):
        """Callback function for scapy sniffer."""
        if not self.is_capturing:
            return
            
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            packet_size = len(packet)
            
            # Determine Protocol
            if TCP in packet:
                protocol = "TCP"
            elif UDP in packet:
                protocol = "UDP"
            elif ICMP in packet:
                protocol = "ICMP"
            else:
                protocol = "OTHER"
                
            # We only train model on TCP, UDP, ICMP for prototype
            if protocol in ["TCP", "UDP", "ICMP"]:
                prediction, confidence = predict_packet(protocol, packet_size)
                
                # Insert into DB
                insert_log(
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    protocol=protocol,
                    packet_size=packet_size,
                    prediction=prediction,
                    confidence_score=confidence
                )
                
                # Terminal alert if attack
                if prediction == "Attack":
                    print(f"[!] ATTACK DETECTED: {src_ip} -> {dst_ip} | Proto: {protocol} | Size: {packet_size} | Conf: {confidence:.2f}")

    def _start_sniffing(self):
        try:
            # Running sniff without count will run until stop_filter returns True
            sniff(prn=self._packet_callback, store=False, stop_filter=lambda x: not self.is_capturing)
        except Exception as e:
            print(f"Scapy sniffing error: {e}")
            self.is_capturing = False

    def start(self):
        if not self.is_capturing:
            print("Starting packet capture...")
            self.is_capturing = True
            self.thread = threading.Thread(target=self._start_sniffing, daemon=True)
            self.thread.start()
            return True
        return False

    def stop(self):
        if self.is_capturing:
            print("Stopping packet capture...")
            self.is_capturing = False
            if self.thread:
                self.thread.join(timeout=2)
            return True
        return False

# Global instance
capture_instance = PacketCapture()
