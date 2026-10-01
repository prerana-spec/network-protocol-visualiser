let currentSteps = [];
let currentStepIndex = -1;
let autoPlayInterval = null;

// Tab Switcher Logic
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (event && event.target) {
        event.target.classList.add('active');
    }
    const tabElement = document.getElementById(tabName);
    if (tabElement) {
        tabElement.classList.add('active');
    }
}

// Main Simulation Fetch Function
async function triggerSimulation(endpoint, payload) {
    stopAutoPlay(); // Stop any active animation loops before loading new data

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            throw new Error(`HTTP Error ${res.status}`);
        }

        const data = await res.json();
        
        const logOutput = document.getElementById('log-output');
        if (logOutput) {
            logOutput.innerText = `[${data.activity}] ${data.details}`;
        }
        
        currentSteps = data.steps || [];
        currentStepIndex = -1;
        renderTimeline();
        nextStep(); // Load step 0 immediately
    } catch (err) {
        console.error("Simulation error:", err);
        alert("Failed to run simulation. Ensure backend server is reachable.");
    }
}

// Action Trigger Handlers
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

// Render Step Cards in Right Panel
function renderTimeline() {
    const timeline = document.getElementById('timeline');
    if (!timeline) return;

    timeline.innerHTML = currentSteps.map((s, i) => {
        const badgeClass = getProtocolBadgeClass(s.protocol);
        return `
            <div class="step-card" id="step-${i}" onclick="jumpToStep(${i})">
                <span class="badge ${badgeClass}">${s.protocol}</span>
                <strong>Step ${s.id || i + 1}:</strong> ${escapeHtml(s.summary)}
            </div>
        `;
    }).join('');
}

// Navigate to Specific Step
function jumpToStep(index) {
    if (index < 0 || index >= currentSteps.length) return;
    currentStepIndex = index;
    
    // Highlight Active Card
    document.querySelectorAll('.step-card').forEach(c => c.classList.remove('active'));
    const activeCard = document.getElementById(`step-${index}`);
    if (activeCard) activeCard.classList.add('active');

    const step = currentSteps[index];
    
    // Update Packet Animation & Badge Text
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

    // Update Inspector Data
    const rawDetails = document.getElementById('raw-details');
    if (rawDetails) {
        rawDetails.innerText = step.raw || step.details || 'No raw data provided.';
    }
}

// Stepper Logic
function nextStep() {
    if (currentStepIndex < currentSteps.length - 1) {
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
        // If at the end, wrap around to start
        if (currentStepIndex >= currentSteps.length - 1) {
            currentStepIndex = -1;
        }
        
        const playBtn = document.getElementById('play-btn');
        if (playBtn) playBtn.innerText = '⏸ Pause';

        autoPlayInterval = setInterval(() => {
            if (currentStepIndex >= currentSteps.length - 1) {
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
    if (currentSteps.length > 0) {
        jumpToStep(0);
    }
}

// Protocol Color Badging Helper
function getProtocolBadgeClass(protocolStr = '') {
    const p = protocolStr.toUpperCase();
    if (p.includes('DNS')) return 'badge-dns';
    if (p.includes('TCP')) return 'badge-tcp';
    if (p.includes('HTTP')) return 'badge-http';
    if (p.includes('SMTP')) return 'badge-smtp';
    return 'badge-default';
}

// HTML Escaping Utility
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}