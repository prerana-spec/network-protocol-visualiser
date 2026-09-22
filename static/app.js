let currentSteps = [];
let currentStepIndex = -1;
let autoPlayInterval = null;

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

async function triggerSimulation(endpoint, payload) {
    const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    document.getElementById('log-output').innerText = `[${data.activity}] ${data.details}`;
    
    currentSteps = data.steps;
    currentStepIndex = -1;
    renderTimeline();
    nextStep();
}

function runBrowse() {
    triggerSimulation('/api/simulate/browse', { url: document.getElementById('browse-url').value });
}

function runMail() {
    triggerSimulation('/api/simulate/mail', {
        to: document.getElementById('mail-to').value,
        subject: document.getElementById('mail-subject').value,
        body: document.getElementById('mail-body').value
    });
}

function runStream() {
    triggerSimulation('/api/simulate/stream', { quality: document.getElementById('stream-quality').value });
}

function renderTimeline() {
    const timeline = document.getElementById('timeline');
    timeline.innerHTML = currentSteps.map((s, i) => `
        <div class="step-card" id="step-${i}" onclick="jumpToStep(${i})">
            <strong>Step ${s.id}: ${s.protocol}</strong> - ${s.summary}
        </div>
    `).join('');
}

function jumpToStep(index) {
    if (index < 0 || index >= currentSteps.length) return;
    currentStepIndex = index;
    
    // Highlight Card
    document.querySelectorAll('.step-card').forEach(c => c.classList.remove('active'));
    const activeCard = document.getElementById(`step-${index}`);
    if (activeCard) activeCard.classList.add('active');

    const step = currentSteps[index];
    
    // Update Packet Animation
    const packet = document.getElementById('packet');
    packet.classList.remove('hidden');
    packet.innerText = step.protocol;
    if (step.direction === 'client-to-server') {
        packet.style.left = '0%';
        setTimeout(() => packet.style.left = '70%', 50);
    } else {
        packet.style.left = '70%';
        setTimeout(() => packet.style.left = '0%', 50);
    }

    // Update Inspector
    document.getElementById('raw-details').innerText = step.raw;
}

function nextStep() {
    if (currentStepIndex < currentSteps.length - 1) jumpToStep(currentStepIndex + 1);
    else clearInterval(autoPlayInterval);
}

function prevStep() {
    if (currentStepIndex > 0) jumpToStep(currentStepIndex - 1);
}

function togglePlay() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        document.getElementById('play-btn').innerText = '▶ Play';
    } else {
        document.getElementById('play-btn').innerText = '⏸ Pause';
        autoPlayInterval = setInterval(() => {
            if (currentStepIndex >= currentSteps.length - 1) {
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
                document.getElementById('play-btn').innerText = '▶ Play';
            } else {
                nextStep();
            }
        }, 1500);
    }
}

function resetTimeline() {
    jumpToStep(0);
}