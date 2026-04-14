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
                label: 'Packets per minute',
                data: [],
                borderColor: '#3B82F6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        if (isCapturing) {
            startPolling();
        }
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
            
            if (isCapturing) {
                startPolling();
            } else {
                stopPolling();
            }
        } else {
            alert(data.message); // e.g. model not trained
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

// Polling Data
function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(() => {
        fetchStats();
        fetchLogs();
    }, 2000);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Fetch Statistics and Update Charts
async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const json = await res.json();
        if (json.status !== 'success') return;
        
        const data = json.data;
        
        // Update Cards - animated counter effect could be added here
        statTotal.textContent = data.total_packets;
        statNormal.textContent = data.total_normal;
        statAttacks.textContent = data.total_attacks;

        // Update Ratio Chart
        ratioChart.data.datasets[0].data = [data.total_normal, data.total_attacks];
        ratioChart.update();

        // Update Traffic Chart
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
        tbody.innerHTML = ''; // Clear current
        
        let recentAttackFound = false;
        
        logs.forEach((log, index) => {
            const tr = document.createElement('tr');
            
            // Format timestamp
            const timeObj = new Date(log.timestamp + "Z"); // SQLite gives UTC implicitly mostly depending on setup, but adding Z handles simple offsets
            const timeStr = timeObj.toLocaleTimeString();

            // Check if attack
            const isAttack = log.prediction === 'Attack';
            if (isAttack && index < 5) recentAttackFound = true; // Check if recent 5 logs have attack
            
            const pillClass = isAttack ? 'pill-attack' : 'pill-normal';
            
            tr.innerHTML = `
                <td>${timeStr}</td>
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
            setTimeout(() => { alertBanner.classList.add('hidden'); }, 3000);
        }

    } catch (e) {
        console.error("Logs fetch error", e);
    }
}

// Initial Boot
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    checkStatus();
    // Fetch once immediately
    fetchStats();
    fetchLogs();
});
