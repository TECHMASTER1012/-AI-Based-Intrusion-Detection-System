const API_BASE = '/api';

// DOM Elements
const btnToggle = document.getElementById('btn-toggle');
const pulseRing = document.querySelector('.pulse-ring');
const alertBanner = document.getElementById('alert-banner');
const alertText = document.getElementById('alert-text');
const tbody = document.querySelector('#logs-table tbody');

// Stats Elements
const statTotal = document.getElementById('stat-total');
const statNormal = document.getElementById('stat-normal');
const statAttacks = document.getElementById('stat-attacks');

// State
let isCapturing = false;
let pollInterval = null;
let alertTimeout = null;
let lastTopLogId = 0;

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
        const res = await fetch(`${API_BASE}/stats`);
        const json = await res.json();
        if (json.status !== 'success') return;
        
        const data = json.data;
        
        statTotal.textContent = data.total_packets;
        statNormal.textContent = data.total_normal;
        statAttacks.textContent = data.total_attacks;

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
        const res = await fetch(`${API_BASE}/logs`);
        const json = await res.json();
        if (json.status !== 'success') return;
        
        const logs = json.data;
        if (!logs || logs.length === 0) return;

        // Only update DOM if new logs arrived
        if (logs[0].id === lastTopLogId) return;
        lastTopLogId = logs[0].id;
        
        tbody.innerHTML = '';
        let recentAttackFound = false;
        
        logs.forEach((log, index) => {
            const tr = document.createElement('tr');
            const isAttack = log.prediction === 'Attack';
            if (isAttack && index < 5) recentAttackFound = true;
            
            const pillClass = isAttack ? 'pill-attack' : 'pill-normal';
            
            tr.innerHTML = `
                <td style="font-weight: 500; font-family: monospace;">${log.timestamp}</td>
                <td>${log.source_ip}</td>
                <td>${log.destination_ip}</td>
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


