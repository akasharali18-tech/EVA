// Initialize Socket.IO connection
const socket = io();

let isActive = false;

// Socket event handlers
socket.on('connect', () => {
    addMessage('SYSTEM', 'Connected to EVA server', 'system-message');
});

socket.on('command_received', (data) => {
    addMessage('YOU', data.command, 'user-message');
});

socket.on('response', (data) => {
    addMessage('EVA', data.message, 'bot-message');
});

socket.on('activated', () => {
    isActive = true;
    updateStatus(true);
});

socket.on('deactivated', () => {
    isActive = false;
    updateStatus(false);
});

// Functions
function toggleActivation() {
    const btn = document.getElementById('activate-btn');
    
    if (!isActive) {
        socket.emit('activate');
        btn.innerHTML = '<span class="btn-icon">🔴</span> DEACTIVATE EVA';
        btn.classList.add('active');
    } else {
        socket.emit('deactivate');
        btn.innerHTML = '<span class="btn-icon">🎤</span> ACTIVATE EVA';
        btn.classList.remove('active');
    }
}

function updateStatus(active) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.getElementById('status-text');
    
    if (active) {
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'ACTIVE - LISTENING';
    } else {
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'INACTIVE';
    }
}

function addMessage(sender, text, type) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <span class="message-sender">${sender}:</span>
        <span class="message-text">${text}</span>
    `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function openManualInput() {
    const modal = document.getElementById('manual-modal');
    modal.classList.add('show');
    document.getElementById('manual-input').focus();
}

function closeManualInput() {
    const modal = document.getElementById('manual-modal');
    modal.classList.remove('show');
    document.getElementById('manual-input').value = '';
}

function submitManualCommand() {
    const input = document.getElementById('manual-input');
    const command = input.value.trim();
    
    if (command) {
        socket.emit('manual_command', { command: command });
        closeManualInput();
    }
}

function clearChat() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = '';
    addMessage('SYSTEM', 'Chat cleared', 'system-message');
}

// Enter key handling for manual input
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('manual-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitManualCommand();
        }
    });
});