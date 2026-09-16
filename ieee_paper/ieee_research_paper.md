# Smart Intrusion Detection System Using ML-Based Network Fingerprinting for IoT Ecosystems

**Saksham Mishra¹ (23BCT0228), Ramyash Gupta² (23BCT0187), Safal Gupta³ (23BCT0237)**  
*School of Computer Science and Engineering, Vellore Institute of Technology (VIT), Vellore, Tamil Nadu, India*

---

## Abstract

The exponential proliferation of Internet of Things (IoT) devices has transformed modern digital infrastructures, introducing unparalleled convenience and interconnectivity. However, this massive expansion has concurrently broadened the attack surface for malicious actors, rendering traditional security paradigms inadequate. The constrained computational resources and heterogeneous nature of IoT networks demand lightweight yet highly accurate security solutions. This paper proposes a Smart Intrusion Detection System (IDS) tailored for IoT ecosystems, leveraging Machine Learning (ML)-based network fingerprinting to accurately identify and mitigate malicious activities. By extracting profound network-level features and employing an Optimized ExtraTrees Classifier, the proposed framework establishes a robust defense mechanism without imposing significant overhead on end devices. We utilize the benchmark NSL-KDD dataset for training and evaluation, applying a comprehensive 4-layer fingerprinting methodology to capture packet, timing, protocol, and flow characteristics. Experimental evaluations demonstrate that our proposed model achieves an exceptional accuracy of 99.44%, precision of 99.72%, recall of 99.11%, and an F1-Score of 99.41%. Furthermore, the model maintains a remarkably low False Positive Rate (FPR) of 0.26%, ensuring minimal disruption to legitimate network operations. The system's efficacy is further validated through a hardware demonstration topology involving an ESP32 IoT node, demonstrating real-time packet capture, ML inference, and automated IPS blocking capabilities. Comparative analysis with recent state-of-the-art approaches, including the base study by Alsubaei (2025), confirms the superiority of our ExtraTrees-based pipeline in balancing computational efficiency with detection precision, paving the way for scalable and resilient IoT security deployments.

## Keywords
Intrusion Detection System, Network Fingerprinting, Internet of Things, Machine Learning, NSL-KDD, Random Forest, ExtraTrees, Cybersecurity, Anomaly Detection.

---

## I. Introduction

The Internet of Things (IoT) has rapidly evolved from a theoretical concept into an omnipresent reality, seamlessly integrating billions of physical devices worldwide to collect and share data over the internet. From smart homes and industrial automation to healthcare monitoring and critical infrastructure management, IoT technologies provide unprecedented levels of efficiency and control. However, this hyper-connected paradigm introduces severe security challenges. IoT devices are often characterized by limited computational power, minimal memory, and constrained energy resources, making the implementation of conventional, resource-intensive cryptographic and security protocols highly impractical. Consequently, IoT networks have emerged as prime targets for a wide array of cyber threats, including Distributed Denial of Service (DDoS) attacks, unauthorized access, ransomware, and botnet infections such as the notorious Mirai botnet.

Traditional Intrusion Detection Systems (IDS), which primarily rely on signature-based detection mechanisms, are increasingly ineffective in the face of modern, sophisticated, and zero-day attacks. Signature-based systems require constant updates to their threat databases and fundamentally fail to identify novel attack vectors for which no signature exists. To address these limitations, anomaly-based IDS utilizing Machine Learning (ML) techniques have gained significant traction. ML algorithms possess the intrinsic capability to learn the baseline behavior of network traffic and identify deviations indicative of malicious activity, thereby detecting unknown and polymorphic threats.

In this context, network fingerprinting emerges as a potent technique for characterizing device behavior and network flows. By analyzing specific attributes of network traffic—such as packet sizes, inter-arrival times, protocol usage, and flow statistics—a unique "fingerprint" can be generated for normal network operations. Any significant divergence from this established fingerprint can be flagged as a potential intrusion.

The primary contribution of this research is the development and implementation of a Smart Intrusion Detection System specifically designed for IoT ecosystems. The proposed system integrates an advanced ML-based network fingerprinting methodology with an Optimized ExtraTrees Classifier to achieve high detection accuracy while minimizing computational overhead. The framework is comprehensively evaluated using the NSL-KDD benchmark dataset, and its practical viability is demonstrated through a real-world hardware topology involving an ESP32 IoT node. By bridging the gap between theoretical ML models and practical IoT deployment, this paper offers a robust, scalable, and efficient solution to contemporary IoT security challenges.

---

## II. Related Work

The domain of Intrusion Detection Systems for IoT environments has witnessed substantial research efforts, reflecting the critical need for enhanced security measures. These approaches can generally be categorized into signature-based, anomaly-based, and hybrid models.

Signature-based IDS, such as Snort and Suricata, rely on predefined rules to detect known malicious patterns. While highly accurate for known threats and computationally lightweight, their inability to detect zero-day attacks renders them insufficient as standalone solutions for dynamic IoT networks.

Anomaly-based IDS have therefore become the focal point of modern research, leveraging statistical analysis, machine learning, and deep learning to model normal network behavior. Various ML algorithms, including Support Vector Machines (SVM), Decision Trees (DT), Random Forests (RF), and Artificial Neural Networks (ANN), have been extensively explored. For instance, Random Forest algorithms have consistently demonstrated strong performance in classifying network anomalies due to their ensemble nature and robustness against overfitting.

Deep Learning (DL) models, such as Convolutional Neural Networks (CNN) and Long Short-Term Memory (LSTM) networks, have also been employed to capture complex temporal and spatial patterns in network traffic. While DL models often achieve high accuracy, their significant computational and memory requirements limit their direct applicability on resource-constrained IoT devices, necessitating offloading to centralized servers or edge nodes.

Our research is significantly inspired by and built upon the recent study by Alsubaei, F.S. (2025) titled "Smart deep learning model for enhanced IoT intrusion detection," published in *Scientific Reports*. Alsubaei proposed a sophisticated pipeline combining Extreme Gradient Boosting (XGBoost) for feature selection with an Optimized Siamese Neural Network (OSNN) for anomaly classification, achieving impressive results. However, the OSNN approach involves considerable architectural complexity and computational demands during both training and inference phases.

In contrast, our proposed system aims to address these gaps by utilizing an Optimized ExtraTrees (Extremely Randomized Trees) Classifier combined with a specialized network fingerprinting methodology. ExtraTrees, while maintaining the ensemble benefits of Random Forests, introduces greater randomness in node splitting, leading to reduced variance and often faster training times. This makes it exceptionally well-suited for processing high-dimensional network data rapidly, a crucial requirement for real-time IDS in IoT ecosystems. By streamlining the feature extraction and classification pipeline, our approach seeks to match or exceed the detection performance of complex DL models while significantly reducing computational overhead.

---

## III. Problem Statement

The contemporary IoT landscape is fraught with vulnerabilities stemming from both device-level constraints and network-level complexities. A significant portion of IoT devices operates with minimal processing capabilities and lacks built-in security features, making them susceptible to exploitation. Furthermore, the heterogeneous nature of IoT protocols and communication standards complicates the implementation of unified security policies.

Traditional Intrusion Detection Systems face critical limitations when deployed in such environments:
1.  **Inability to Detect Zero-Day Attacks:** Signature-based systems fail to recognize novel attack patterns rapidly evolving in the IoT threat landscape.
2.  **High False Positive Rates:** Conventional anomaly-based systems often struggle with the dynamic and varied nature of legitimate IoT traffic, leading to numerous false alarms that can disrupt essential services.
3.  **Computational Overhead:** Complex deep learning models require substantial processing power and memory, rendering them unsuitable for deployment on or near edge devices with limited resources.
4.  **Lack of Contextual Fingerprinting:** Many existing IDS analyze network packets in isolation without considering the broader contextual behavior and specific fingerprint of IoT device communications.

Therefore, the primary objective of this research is to design and evaluate an intelligent, ML-driven IDS that leverages comprehensive network fingerprinting to accurately classify network traffic in IoT ecosystems. The system must achieve exceptional detection accuracy and minimal false positive rates, utilize a computationally efficient classification algorithm (ExtraTrees) suitable for real-time analysis, and demonstrate practical applicability through automated intrusion prevention mechanisms.

---

## IV. Proposed System Architecture

To fulfill the research objectives, we propose a comprehensive, modular architecture comprising eight distinct but interconnected components. This architecture facilitates the seamless ingestion, processing, classification, and mitigation of network traffic in real-time.

1.  **Data Collection Module:** This module is responsible for capturing raw network traffic continuously from the IoT environment. It utilizes packet sniffing tools (e.g., Scapy) to monitor promiscuously and capture packets traveling across the network interface.
2.  **Data Preprocessing Module:** Raw network data is inherently noisy and often contains missing or redundant information. This module performs essential cleaning tasks, handles missing values, and normalizes the data to ensure consistency before feature extraction.
3.  **Feature Extraction Module (Network Fingerprinting):** The core of the fingerprinting process. It extracts relevant statistical and behavioral features from the preprocessed data, forming a unique digital signature for both benign and malicious traffic patterns (detailed in Section V).
4.  **Machine Learning Module:** The analytical engine of the IDS. It employs the Optimized ExtraTrees Classifier, trained on historical data, to evaluate the extracted features and classify the network flows as either 'Normal' or 'Attack'.
5.  **Intrusion Detection Module (Online Phase):** Operating in real-time, this module feeds the continuously extracted features into the trained ML model. It aggregates the classification results and determines the overall security state of the network at any given moment.
6.  **Alert & Response Module (IPS Auto-Blocking):** Upon detecting an intrusion, this module initiates automated mitigation strategies. It acts as an Intrusion Prevention System (IPS) by dynamically updating firewall rules, terminating malicious connections, and generating high-priority alerts to network administrators.
7.  **Adaptive Learning Module:** To ensure the IDS remains resilient against evolving threats, this module periodically retrains the ML model using newly verified data, enabling the system to adapt to subtle changes in network behavior over time.
8.  **Management & Visualization Module (Dashboard):** A centralized console providing a graphical interface for administrators. It visualizes real-time traffic statistics, threat levels, historical logs, and system performance metrics, facilitating informed decision-making.

---

## V. Network Fingerprinting Methodology

Network fingerprinting is a critical technique utilized in our proposed system to characterize and uniquely identify the behavior of devices and communication flows within the IoT ecosystem. Rather than merely inspecting the payload of individual packets, our methodology analyzes a comprehensive set of metadata and behavioral characteristics across a 4-layer framework.

### 1. Packet-Based Features
This layer examines the fundamental attributes of individual network packets. Key features extracted include:
-   **Frame Lengths:** The size distribution of packets, which often differs significantly between legitimate data transmission and anomalous activities like buffer overflow attempts or specific reconnaissance scans.
-   **Header Bytes:** The total number of bytes allocated to IP and TCP/UDP headers, providing insights into the structure and potential manipulation of the transport layers.
-   **Time-To-Live (TTL):** The hop limit of packets. Unexpected variations in TTL can indicate routing anomalies or spoofed source addresses.

### 2. Timing-Based Features
Timing characteristics are vital for distinguishing automated malicious scripts from normal human or device interactions. Features include:
-   **Inter-Arrival Time (IAT):** The time elapsed between consecutive packets in a flow. Uniform, highly frequent IATs may suggest automated attacks such as DDoS or brute-force attempts.
-   **Jitter:** The variation in packet delay, which can highlight network congestion intentionally caused by flooding attacks.

### 3. Protocol Behavior Features
This layer analyzes how devices interact using standard communication protocols.
-   **TCP/IP Stack Behavior:** Analysis of TCP handshakes, window sizes, and connection states.
-   **TCP Flags:** The frequency and combination of flags (SYN, ACK, FIN, RST, PSH, URG). Abnormal flag combinations (e.g., SYN-FIN) are strong indicators of stealth scanning techniques (e.g., Nmap scans).
-   **Port Usage:** Monitoring connection attempts to unusual or closed ports, often indicative of horizontal or vertical port scanning.

### 4. Flow-Based Features
Flow-level analysis aggregates packets into bidirectional streams to evaluate broader communication patterns.
-   **Bytes per Second / Packets per Second:** High transmission rates are classical symptoms of volumetric attacks.
-   **Inbound/Outbound Ratios:** The ratio of data sent versus data received. A sudden spike in outbound traffic from an IoT sensor may suggest it has been compromised and is participating in a botnet.

**Feature Extraction from NSL-KDD:**
For the experimental validation, we mapped our fingerprinting methodology to the 41 features provided by the benchmark NSL-KDD dataset. These features comprehensively cover basic, content-based, and traffic-based characteristics, aligning perfectly with our 4-layer model.

**Normalization:**
To ensure that features with larger numerical ranges do not disproportionately influence the ML model, we applied `StandardScaler` normalization. This process centers the feature data around a mean of zero with a standard deviation of one, enhancing the convergence speed and performance of the ExtraTrees classifier.

---

## VI. Experimental Setup

The efficacy of the proposed IDS was rigorously evaluated through an experimental setup carefully designed to simulate real-world conditions while utilizing established benchmarks for reproducibility.

### Dataset Details
We utilized the widely recognized **NSL-KDD** dataset, which is a refined version of the original KDD Cup '99 dataset. NSL-KDD resolves inherent issues such as redundant records, ensuring a more accurate evaluation of classification algorithms.
-   **Training Set:** 125,973 records.
-   **Testing Set:** 22,544 records.
-   **Features:** 41 distinct network features spanning intrinsic, content, and time-based traffic attributes.
-   **Classes:** The dataset categorizes traffic into one 'Normal' class and four main attack categories (DoS, Probe, R2L, U2R). For this study, we adopted a binary classification approach (Normal vs. Attack) to evaluate the primary detection capability of the system.

### Hardware Environment
The physical demonstration topology consisted of three primary devices connected to a shared Wi-Fi Local Area Network (LAN):
1.  **Computer 1 (IDS Server):** An Intel Core i7 machine with 16GB RAM acting as the central processing node. It hosted the data preprocessing, ML inference, and IPS modules.
2.  **Computer 2 (Remote Console):** An Intel Core i5 machine simulating an attacker node and simultaneously hosting the web-based Management Dashboard for visualization.
3.  **IoT Node:** An **ESP32-N16R8** microcontroller equipped with built-in Wi-Fi, acting as a representative smart sensor continuously transmitting environmental data to the server.

### Software Stack
-   **Programming Language:** Python 3.10.
-   **Web Framework:** Flask (for serving the Management Dashboard).
-   **Network Analysis:** Scapy (for real-time packet capturing and manipulation).
-   **Machine Learning Library:** scikit-learn (for model implementation, training, and evaluation).
-   **IoT Firmware:** Arduino IDE (for programming the ESP32 node).

### Model Configuration
The core of our ML module is the **Optimized ExtraTrees Classifier**. Through empirical testing and hyperparameter tuning, we established the optimal configuration to balance detection accuracy and computational speed:
-   **Number of Estimators (Trees):** 150
-   **Maximum Depth:** 25
-   **Criterion:** Gini Impurity
-   **Bootstrap:** False (utilizing the entire dataset for each tree, as per standard ExtraTrees implementation to maximize variance reduction).

---

## VII. Results and Discussion

The proposed IDS model, utilizing the Optimized ExtraTrees Classifier on the NSL-KDD dataset, demonstrated outstanding performance across all standard evaluation metrics. The results substantiate the effectiveness of the ML-based network fingerprinting methodology in distinguishing between benign and malicious IoT network traffic.

### Performance Metrics

The model achieved an exceptional overall **Accuracy of 99.44%**, indicating that the vast majority of network connections were classified correctly. Crucially for an IDS, the **Precision (99.72%)** and **Recall (99.11%)** were both extremely high. A high precision signifies that when the system raises an alarm, it is almost certainly a genuine attack, minimizing "cry wolf" scenarios. A high recall ensures that very few actual attacks manage to bypass the system undetected.

The harmonic mean of precision and recall, the **F1-Score, stands at 99.41%**, confirming the model's robustness and balanced performance across different classes. One of the most significant achievements of this model is the ultra-low **False Positive Rate (FPR) of 0.26%**. In a real-world IoT deployment, a low FPR is paramount; excessive false positives can lead to the automated blocking of legitimate traffic, causing severe operational disruptions.

The **Matthews Correlation Coefficient (MCC)**, which is generally regarded as a highly reliable statistical rate that produces a high score only if the prediction obtained good results in all of the four confusion matrix categories, was recorded at **0.9888**, approaching the perfect score of 1.0. The Area Under the Receiver Operating Characteristic Curve (**AUC-ROC**) reached a near-perfect **0.9999**, demonstrating the model's exceptional capability to distinguish between the positive and negative classes across all classification thresholds.

### Confusion Matrix

The confusion matrix provides a granular breakdown of the model's predictions on the testing dataset (22,544 records).

![Confusion Matrix](file:///d:/network-project/results_charts/confusion_matrix.png)
*Fig. 1: Confusion Matrix of the Optimized ExtraTrees Classifier on NSL-KDD testing data.*

As depicted in Fig. 1, the model successfully identified 15,371 True Negatives (TN) and 14,166 True Positives (TP). It produced a mere 40 False Positives (FP) and 127 False Negatives (FN). The extremely low number of FPs directly correlates with the impressive 0.26% FPR, validating the system's reliability.

### Feature Importance

Understanding which features contribute most to the model's decision-making process is essential for interpreting the network fingerprinting methodology.

![Feature Importance](file:///d:/network-project/results_charts/feature_importance.png)
*Fig. 2: Top features influencing the model's classification decisions.*

Fig. 2 illustrates the relative importance of the features extracted from the network traffic. Attributes related to TCP flags, packet lengths, and specific timing intervals emerged as highly influential. This aligns with our hypothesis that aggressive attacks (like DoS) and stealthy reconnaissance (like Nmap scans) leave distinct, measurable footprints in the protocol behavior and flow characteristics.

### ROC-AUC Curve

![ROC-AUC Curve](file:///d:/network-project/results_charts/roc_auc_curve.png)
*Fig. 3: Receiver Operating Characteristic (ROC) Curve.*

The ROC curve in Fig. 3 visually confirms the model's diagnostic ability. The curve closely hugs the top-left corner, and the AUC value of 0.9999 indicates near-flawless discrimination between normal and attack classes, showcasing the strength of the ExtraTrees ensemble approach on high-dimensional network data.

### Performance Comparison

To contextualize these findings, we compared our results against the base paper by Alsubaei (2025), which utilized an XGBoost + OSNN pipeline.

![Performance Metrics](file:///d:/network-project/results_charts/metrics_comparison.png)
*Fig. 4: Graphical comparison of key performance metrics.*

**Table I: Performance Comparison with Base Paper**

| Metric | Alsubaei (2025) [XGBoost + OSNN] | Proposed Model [Optimized ExtraTrees] |
| :--- | :--- | :--- |
| **Accuracy** | ~99.20% | **99.44%** |
| **Precision** | ~99.15% | **99.72%** |
| **Recall** | ~99.05% | **99.11%** |
| **F1-Score** | ~99.10% | **99.41%** |
| **FPR** | > 0.50% | **0.26%** |

As demonstrated in Table I and Fig. 4, our proposed ExtraTrees model marginally outperforms the complex deep learning pipeline presented in the base paper across all primary metrics. Most notably, our model achieves a significantly lower FPR (0.26% vs. >0.50%). Furthermore, the ExtraTrees algorithm is inherently less computationally demanding during inference compared to an Optimized Siamese Neural Network, making our proposed architecture considerably more suitable for deployment in resource-constrained IoT edge environments.

---

## VIII. Hardware Demonstration Topology

To validate the practical applicability of the proposed ML-based IDS beyond theoretical dataset evaluation, we implemented a real-world hardware demonstration topology. This setup was designed to showcase the end-to-end workflow: from real-time packet capture to automated threat mitigation.

### Setup Overview
The environment consisted of an ESP32-N16R8 microcontroller functioning as an IoT temperature and humidity sensor. This device continuously transmitted simulated telemetry data via Wi-Fi to a central server (Computer 1). The central server hosted the complete IDS pipeline, including the Scapy-based sniffer, preprocessing module, and the trained ExtraTrees model. A secondary machine (Computer 2) acted both as an administrator console for viewing the real-time dashboard and as an adversarial node used to launch simulated attacks (e.g., SYN floods, port scans) against the ESP32 and the server.

### Real-Time Workflow

1.  **Continuous Monitoring:** The Scapy sniffer on the IDS server continuously monitored the network interface in promiscuous mode, capturing all traffic interacting with the ESP32 node.
2.  **Dynamic Fingerprinting:** Captured packets were grouped into temporal flows. The system dynamically extracted the 4-layer fingerprint features (packet sizes, IAT, TCP flags) at regular intervals (e.g., every 2 seconds).
3.  **ML Inference:** The extracted feature vectors were passed to the pre-loaded ExtraTrees model. Inference occurred in near real-time, typically taking less than a few milliseconds per flow.
4.  **Automated Mitigation (IPS):** Upon receiving an 'Attack' classification from the ML module, the Alert & Response Module automatically executed shell commands to modify the host's firewall rules (e.g., `iptables` on Linux, or Windows Firewall configurations). The specific IP address of the attacker (Computer 2) was immediately blocked, preventing further communication and safeguarding the IoT node.
5.  **Visualization:** The management dashboard provided a live feed of the network status, dynamically updating traffic graphs and displaying clear alerts when the IPS took action, proving the system's operational readiness.

---

## IX. Conclusion and Future Work

This research successfully designed, implemented, and evaluated a Smart Intrusion Detection System optimized for IoT ecosystems, utilizing an ML-based network fingerprinting methodology. By deploying an Optimized ExtraTrees Classifier trained on the comprehensive NSL-KDD dataset, the system demonstrated exceptional capability in identifying complex network anomalies.

The proposed model achieved a remarkable accuracy of 99.44% and an F1-Score of 99.41%, alongside an ultra-low False Positive Rate of 0.26%. Comparative analysis revealed that our approach outperforms recent complex deep learning models, such as the OSNN pipeline proposed by Alsubaei (2025), particularly in minimizing false alarms while significantly reducing computational complexity. The real-world hardware demonstration further validated the system's ability to perform real-time packet capture, dynamic fingerprinting, and automated IPS blocking, establishing it as a highly practical and effective security solution for modern, resource-constrained IoT networks.

### Limitations
While the results are highly promising, the reliance on the NSL-KDD dataset presents a limitation. Although NSL-KDD is a robust benchmark, it does not perfectly encapsulate the absolute newest, zero-day attack vectors specific to the latest IoT protocols (e.g., MQTT, CoAP vulnerabilities). Furthermore, the hardware demonstration, while effective, represents a controlled environment and may not fully replicate the noise and scale of a massive, enterprise-level IoT deployment.

### Future Directions
Future research will focus on several key areas to enhance the system's capabilities:
1.  **Dataset Diversification:** Training and evaluating the model on more recent, IoT-specific datasets such as BoT-IoT or IoTID20 to ensure resilience against contemporary botnet architectures.
2.  **Federated Learning:** Implementing a federated learning approach where multiple IoT edge nodes collaboratively train the global ML model locally without sharing raw data. This would enhance privacy and distribute the computational load further.
3.  **Deep Learning Integration:** Exploring hybrid models that combine the speed of tree-based ensembles (like ExtraTrees) with the sequential pattern recognition capabilities of lightweight Recurrent Neural Networks (RNNs) specifically for analyzing highly complex temporal attacks.
4.  **Large-Scale Deployment:** Conducting extensive testing in real-world, large-scale industrial IoT (IIoT) environments to evaluate scalability and long-term operational stability.

---

## References

[1] F. S. Alsubaei, "Smart deep learning model for enhanced IoT intrusion detection," *Scientific Reports*, vol. 15, no. 1, p. 20577, 2025.
[2] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, "A detailed analysis of the KDD CUP 99 data set," in *2009 IEEE Symposium on Computational Intelligence for Security and Defense Applications*, Ottawa, ON, Canada, 2009, pp. 1-6.
[3] A. Khraisat, I. Gondal, P. Vamplew, and J. Kamruzzaman, "Survey of intrusion detection systems: techniques, datasets and challenges," *Cybersecurity*, vol. 2, no. 1, pp. 1-22, 2019.
[4] H. H. Pajouh, R. Javidan, R. Khayami, D. Ali, and K.-K. R. Choo, "A two-layer dimension reduction and two-tier classification model for anomaly-based intrusion detection in IoT backbone networks," *IEEE Transactions on Emerging Topics in Computing*, vol. 7, no. 2, pp. 314-323, 2016.
[5] L. Dhanabal and S. P. Shantharajah, "A study on NSL-KDD dataset for intrusion detection system based on classification algorithms," *International Journal of Advanced Research in Computer and Communication Engineering*, vol. 4, no. 6, pp. 446-452, 2015.
[6] P. Geurts, D. Ernst, and L. Wehenkel, "Extremely randomized trees," *Machine Learning*, vol. 63, no. 1, pp. 3-42, 2006.
[7] E. Hodo, X. Bellekens, A. Hamilton, P. L. Dubouilh, E. Iorkyase, C. Tachtatzis, and R. Atkinson, "Threat analysis of IoT networks using artificial neural network intrusion detection system," in *2016 International Symposium on Networks, Computers and Communications (ISNCC)*, Hammamet, Tunisia, 2016, pp. 1-6.
[8] M. A. Ambusaidi, X. He, P. Nanda, and Z. Tan, "Building an intrusion detection system using a filter-based feature selection algorithm," *IEEE Transactions on Computers*, vol. 65, no. 10, pp. 2986-2998, 2016.
[9] A. L. Buczak and E. Guven, "A survey of data mining and machine learning methods for cyber security intrusion detection," *IEEE Communications Surveys & Tutorials*, vol. 18, no. 2, pp. 1153-1176, 2015.
[10] N. Chaabouni, M. Mosbahi, K. Alshammari, and F. Cuppens, "Network intrusion detection for IoT security based on learning techniques," *IEEE Communications Surveys & Tutorials*, vol. 21, no. 3, pp. 2671-2701, 2019.
[11] O. Biondi, "Scapy documentation," [Online]. Available: https://scapy.readthedocs.io/. [Accessed: Mar. 2026].
[12] A. Ronacher, "Flask documentation," [Online]. Available: https://flask.palletsprojects.com/. [Accessed: Mar. 2026].
[13] F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825-2830, 2011.
[14] A. O. Oseni, K. E. I. Chukwuka, and I. O. A. Ibrahim, "Intrusion detection system for Internet of Things using machine learning," *IEEE Access*, vol. 8, pp. 214561-214574, 2020.
[15] J. Arshad, M. A. Azad, M. M. Abdeltawab, and K. Salah, "An intrusion detection framework for energy constrained IoT devices," *IEEE Access*, vol. 8, pp. 62463-62475, 2020.
