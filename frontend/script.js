const API_BASE = '/api';

// DOM Elements
const btnToggle = document.getElementById('btn-toggle');
const pulseRing = document.querySelector('.pulse-ring');
const alertBanner = document.getElementById('alert-banner');
const alertText = document.getElementById('alert-text');
const tbody = document.querySelector('#logs-table tbody');

// IP Search & Tracer Elements
const ipSearchInput = document.getElementById('ip-search-input');
const btnSearchIp = document.getElementById('btn-search-ip');
const ipTracerBar = document.getElementById('ip-tracer-bar');
const tracerIpDisplay = document.getElementById('tracer-ip-display');
const tracerCountBadge = document.getElementById('tracer-count-badge');
const btnClearIp = document.getElementById('btn-clear-ip');
const chartTrafficTitle = document.getElementById('chart-traffic-title');

// Stats Elements
const statTotal = document.getElementById('stat-total');
const statNormal = document.getElementById('stat-normal');
const statAttacks = document.getElementById('stat-attacks');

// State
let isCapturing = false;
let pollInterval = null;
let alertTimeout = null;
let lastTopLogId = 0;
let followedIP = null;

// Follow IP Logic
function followIP(ip) {
    if (!ip || !ip.trim()) return;
    followedIP = ip.trim();
    ipSearchInput.value = followedIP;
    
    // UI Banner Updates
    tracerIpDisplay.textContent = followedIP;
    ipTracerBar.classList.remove('hidden');
    chartTrafficTitle.textContent = `Traffic Flow (${followedIP})`;
    
    // Reset log diff check & trigger immediate refresh
    lastTopLogId = 0;
    fetchStats();
    fetchLogs();
}

function clearIPFilter() {
    followedIP = null;
    ipSearchInput.value = '';
    ipTracerBar.classList.add('hidden');
    chartTrafficTitle.textContent = 'Traffic Flow (Real-Time)';
    
    lastTopLogId = 0;
    fetchStats();
    fetchLogs();
}

// Global window exposure for inline onclick handlers
window.followIP = followIP;

// IP Filter Event Listeners
btnSearchIp.addEventListener('click', () => {
    followIP(ipSearchInput.value);
});

ipSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        followIP(ipSearchInput.value);
    }
});

btnClearIp.addEventListener('click', () => {
    clearIPFilter();
});

// Chart Instances
let trafficChart, ratioChart;

// Initialize Charts with sleek dark theme configurations
function initCharts() {
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Outfit', sans-serif";

    const ctxTraffic = document.getElementById('trafficChart').getContext('2d');
    trafficChart = new Chart(ctxTraffic, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Packets per sec',
                data: [],
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.15)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.3,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 250 },
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });

    const ctxRatio = document.getElementById('ratioChart').getContext('2d');
    ratioChart = new Chart(ctxRatio, {
        type: 'doughnut',
        data: {
            labels: ['Normal', 'Threat'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#10B981', '#EF4444'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            animation: { duration: 300 },
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// Fetch Initial Status
async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        isCapturing = data.is_capturing;
        updateUIButtonState();
    } catch (e) {
        console.error("Failed to check status", e);
    }
}

// Button Toggle Logic
btnToggle.addEventListener('click', async () => {
    const endpoint = isCapturing ? '/stop_capture' : '/start_capture';
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
        const data = await res.json();
        
        if (data.status === 'success') {
            isCapturing = !isCapturing;
            updateUIButtonState();
            fetchStats();
            fetchLogs();
        } else {
            alert(data.message);
        }
    } catch (e) {
        console.error("Action failed", e);
    }
});

function updateUIButtonState() {
    if (isCapturing) {
        btnToggle.textContent = 'Stop Capture';
        btnToggle.classList.remove('btn-primary');
        btnToggle.classList.add('btn-danger');
        pulseRing.classList.add('capturing');
    } else {
        btnToggle.textContent = 'Start Capture';
        btnToggle.classList.remove('btn-danger');
        btnToggle.classList.add('btn-primary');
        pulseRing.classList.remove('capturing');
    }
}

// Polling Data at 400ms for Sub-Second Real-Time Responsiveness
function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => {
        checkStatus();
        fetchStats();
        fetchLogs();
    }, 400);
}

// Fetch Statistics and Update Charts
async function fetchStats() {
    try {
        const queryParam = followedIP ? `?ip=${encodeURIComponent(followedIP)}` : '';
        const res = await fetch(`${API_BASE}/stats${queryParam}`);
        const json = await res.json();
        if (json.status !== 'success') return;
        
        const data = json.data;
        
        statTotal.textContent = data.total_packets;
        statNormal.textContent = data.total_normal;
        statAttacks.textContent = data.total_attacks;

        if (followedIP) {
            tracerCountBadge.textContent = `${data.total_packets} Packets Scanned (${data.total_attacks} Threats)`;
        }

        // Update Ratio Chart
        ratioChart.data.datasets[0].data = [data.total_normal, data.total_attacks];
        ratioChart.update();

        // Update Traffic Chart (Real-time per second)
        const times = data.time_series.map(t => t.time);
        const counts = data.time_series.map(t => t.count);
        trafficChart.data.labels = times;
        trafficChart.data.datasets[0].data = counts;
        trafficChart.update();

    } catch (e) {
        console.error("Stats fetch error", e);
    }
}

// Fetch Logs and Update Table
async function fetchLogs() {
    try {
        const queryParam = followedIP ? `?ip=${encodeURIComponent(followedIP)}` : '';
        const res = await fetch(`${API_BASE}/logs${queryParam}`);
        const json = await res.json();
        if (json.status !== 'success') return;
        
        const logs = json.data;
        if (!logs) return;

        if (logs.length > 0 && logs[0].id === lastTopLogId) return;
        if (logs.length > 0) lastTopLogId = logs[0].id;
        
        tbody.innerHTML = '';
        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-sec); padding: 2rem;">No packet logs captured for IP: <strong>${followedIP}</strong></td></tr>`;
            return;
        }

        let recentAttackFound = false;
        
        logs.forEach((log, index) => {
            const tr = document.createElement('tr');
            const isAttack = log.prediction === 'Attack';
            if (isAttack && index < 5) recentAttackFound = true;
            
            const pillClass = isAttack ? 'pill-attack' : 'pill-normal';
            
            tr.innerHTML = `
                <td style="font-weight: 500; font-family: monospace;">${log.timestamp}</td>
                <td><span class="ip-tag" onclick="followIP('${log.source_ip}')" title="Click to follow ${log.source_ip}">${log.source_ip}</span></td>
                <td><span class="ip-tag" onclick="followIP('${log.destination_ip}')" title="Click to follow ${log.destination_ip}">${log.destination_ip}</span></td>
                <td>${log.protocol}</td>
                <td>${log.packet_size} B</td>
                <td><span class="pill ${pillClass}">${log.prediction}</span></td>
                <td>${(log.confidence_score * 100).toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
        
        // Handle Alert Banner
        if (recentAttackFound) {
            alertBanner.classList.remove('hidden');
            if (alertTimeout) clearTimeout(alertTimeout);
            alertTimeout = setTimeout(() => { alertBanner.classList.add('hidden'); }, 3000);
        }

    } catch (e) {
        console.error("Logs fetch error", e);
    }
}

// Initial Boot
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    checkStatus();
    fetchStats();
    fetchLogs();
    startPolling();
});



