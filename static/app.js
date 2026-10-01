let currentSteps = [];
let filteredSteps = [];
let currentStepIndex = -1;
let autoPlayInterval = null;
let activeFilter = 'all';

// Tab Switcher Logic
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (window.event && window.event.target) {
        window.event.target.classList.add('active');
    }
    const tabElement = document.getElementById(tabName);
    if (tabElement) {
        tabElement.classList.add('active');
    }
}

// Layer View Filter Switching Logic
function filterLayerView(layer) {
    activeFilter = layer;
    document.querySelectorAll('.layer-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`view-${layer}`);
    if (activeBtn) activeBtn.classList.add('active');

    applyFilter();
}

function applyFilter() {
    if (activeFilter === 'all') {
        filteredSteps = [...currentSteps];
    } else {
        filteredSteps = currentSteps.filter(s => s.layer === activeFilter);
    }
    
    renderTimeline();
    if (filteredSteps.length > 0) {
        jumpToStep(0);
    } else {
        const raw = document.getElementById('raw-details');
        if (raw) raw.innerText = "No steps available for this view layer.";
    }
}

// Main Simulation Fetch Function
async function triggerSimulation(endpoint, payload) {
    stopAutoPlay();

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error(`HTTP Error ${res.status}`);

        const data = await res.json();
        
        const logOutput = document.getElementById('log-output');
        if (logOutput) {
            logOutput.innerText = `[${data.activity}] ${data.details}`;
        }
        
        currentSteps = data.steps || [];
        applyFilter();
    } catch (err) {
        console.error("Simulation error:", err);
        alert("Failed to run simulation. Ensure backend server is reachable.");
    }
}

function runBrowse() {
    const urlInput = document.getElementById('browse-url')?.value || 'https://example.com';
    triggerSimulation('/api/simulate/browse', { url: urlInput });
}

function runMail() {
    triggerSimulation('/api/simulate/mail', {
        to: document.getElementById('mail-to')?.value || 'user@example.com',
        subject: document.getElementById('mail-subject')?.value || 'Hello',
        body: document.getElementById('mail-body')?.value || 'Test Message'
    });
}

function runStream() {
    const qualityInput = document.getElementById('stream-quality')?.value || '1080p';
    triggerSimulation('/api/simulate/stream', { quality: qualityInput });
}

// Render Step Cards in Timeline
function renderTimeline() {
    const timeline = document.getElementById('timeline');
    if (!timeline) return;

    if (filteredSteps.length === 0) {
        timeline.innerHTML = `<p>No events recorded for layer: <strong>${activeFilter}</strong></p>`;
        return;
    }

    timeline.innerHTML = filteredSteps.map((s, i) => {
        const badgeClass = getProtocolBadgeClass(s.protocol);
        return `
            <div class="step-card" id="step-${i}" onclick="jumpToStep(${i})">
                <span class="badge ${badgeClass}">${s.protocol}</span>
                <span class="layer-indicator">[${s.layer.toUpperCase()}]</span>
                <strong>Step ${s.id || i + 1}:</strong> ${escapeHtml(s.summary)}
            </div>
        `;
    }).join('');
}

// Navigate to Specific Step
function jumpToStep(index) {
    if (index < 0 || index >= filteredSteps.length) return;
    currentStepIndex = index;
    
    document.querySelectorAll('.step-card').forEach(c => c.classList.remove('active'));
    const activeCard = document.getElementById(`step-${index}`);
    if (activeCard) activeCard.classList.add('active');

    const step = filteredSteps[index];
    
    // Packet Animation Update
    const packet = document.getElementById('packet');
    if (packet) {
        packet.classList.remove('hidden');
        packet.innerText = step.protocol;
        
        if (step.direction === 'client-to-server') {
            packet.style.left = '0%';
            setTimeout(() => { packet.style.left = '70%'; }, 50);
        } else {
            packet.style.left = '70%';
            setTimeout(() => { packet.style.left = '0%'; }, 50);
        }
    }

    // Inspector Data Update
    const rawDetails = document.getElementById('raw-details');
    if (rawDetails) {
        let detailsText = `Layer: ${step.layer.toUpperCase()}\nProtocol: ${step.protocol}\nDirection: ${step.direction}\n`;
        if (step.flags) detailsText += `TCP Flags: ${step.flags}\nSeq: ${step.seq} | Ack: ${step.ack} | Win: ${step.win}\n`;
        detailsText += `\nRaw Details:\n${step.raw}`;
        rawDetails.innerText = detailsText;
    }
}

// Stepper Controls
function nextStep() {
    if (currentStepIndex < filteredSteps.length - 1) {
        jumpToStep(currentStepIndex + 1);
    } else {
        stopAutoPlay();
    }
}

function prevStep() {
    if (currentStepIndex > 0) {
        jumpToStep(currentStepIndex - 1);
    }
}

function togglePlay() {
    if (autoPlayInterval) {
        stopAutoPlay();
    } else {
        if (currentStepIndex >= filteredSteps.length - 1) {
            currentStepIndex = -1;
        }
        
        const playBtn = document.getElementById('play-btn');
        if (playBtn) playBtn.innerText = '⏸ Pause';

        autoPlayInterval = setInterval(() => {
            if (currentStepIndex >= filteredSteps.length - 1) {
                stopAutoPlay();
            } else {
                nextStep();
            }
        }, 1500);
    }
}

function stopAutoPlay() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }
    const playBtn = document.getElementById('play-btn');
    if (playBtn) playBtn.innerText = '▶ Play';
}

function resetTimeline() {
    stopAutoPlay();
    if (filteredSteps.length > 0) {
        jumpToStep(0);
    }
}

function getProtocolBadgeClass(protocolStr = '') {
    const p = protocolStr.toUpperCase();
    if (p.includes('DNS')) return 'badge-dns';
    if (p.includes('TCP')) return 'badge-tcp';
    if (p.includes('UDP')) return 'badge-udp';
    if (p.includes('HTTP')) return 'badge-http';
    if (p.includes('SMTP')) return 'badge-smtp';
    return 'badge-default';
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}