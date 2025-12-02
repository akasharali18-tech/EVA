// Initialize Socket.IO
const socket = io();

// State variables
let isVoiceActive = false;
let isConnected = false;

// ============================================
// SOCKET EVENT HANDLERS (FIXED)
// ============================================

socket.on('connect', () => {
    console.log('✅ Connected to server');
    isConnected = true;
    showNotification('Connected', 'Connected to EVA server', 'success');
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from server');
    isConnected = false;
    showNotification('Disconnected', 'Lost connection to server', 'error');
    if (isVoiceActive) {
        stopVoice();
    }
});

socket.on('voice_started', (data) => {
    console.log('🎤 Voice mode activated');
    updateVoiceUI(true);
    showNotification('Voice Active', 'Say "EVA" followed by your command', 'info');
});

socket.on('voice_stopped', (data) => {
    console.log('🛑 Voice mode stopped');
    updateVoiceUI(false);
});

socket.on('listening_status', (data) => {
    console.log('👂 Status:', data.status);
});

socket.on('speech_recognized', (data) => {
    console.log('🗣️ Recognized:', data.text);
    addMessage('YOU', data.text, 'user-message');
});

socket.on('wake_word_detected', (data) => {
    console.log('👋 Wake word detected');
    addMessage('EVA', data.message, 'bot-message');
});

socket.on('command_response', (data) => {
    console.log('🤖 Response:', data.response);
    addMessage('EVA', data.response, 'bot-message');
});

// ============================================
// VOICE CONTROL FUNCTIONS (FIXED)
// ============================================

function toggleVoice() {
    if (!isConnected) {
        showNotification('Error', 'Not connected to server', 'error');
        return;
    }
    
    if (!isVoiceActive) {
        startVoice();
    } else {
        stopVoice();
    }
}

function startVoice() {
    console.log('🎤 Starting voice...');
    isVoiceActive = true;
    socket.emit('start_voice');
    updateVoiceUI(true);
}

function stopVoice() {
    console.log('🛑 Stopping voice...');
    isVoiceActive = false;
    socket.emit('stop_voice');
    updateVoiceUI(false);
}

function updateVoiceUI(active) {
    const voiceBtn = document.getElementById('voice-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    if (active) {
        voiceBtn.classList.add('active');
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'LISTENING';
        listeningIndicator.classList.add('active');
    } else {
        voiceBtn.classList.remove('active');
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'INACTIVE';
        listeningIndicator.classList.remove('active');
    }
}

// ============================================
// TEXT MESSAGE FUNCTIONS (FIXED)
// ============================================

function sendTextMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    
    if (!text) return;
    
    if (!isConnected) {
        showNotification('Error', 'Not connected to server', 'error');
        return;
    }
    
    console.log('⌨️ Sending:', text);
    
    // Hide welcome message
    hideWelcome();
    
    // Add user message
    addMessage('YOU', text, 'user-message');
    
    // Send to server
    socket.emit('send_text_command', { command: text });
    
    // Clear input
    input.value = '';
    input.focus();
}

function quickCommand(cmd) {
    document.getElementById('chat-input').value = cmd;
    sendTextMessage();
}

// ============================================
// UI FUNCTIONS
// ============================================

function addMessage(sender, text, type) {
    const container = document.getElementById('chat-container');
    
    // Hide welcome on first message
    hideWelcome();
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.innerHTML = `
        <span class="message-sender">${sender}:</span>
        <span class="message-text">${text}</span>
    `;
    
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function hideWelcome() {
    const welcome = document.getElementById('welcome-message');
    if (welcome && welcome.style.display !== 'none') {
        welcome.style.display = 'none';
    }
}

function clearChat() {
    const container = document.getElementById('chat-container');
    container.innerHTML = `
        <div class="welcome-message" id="welcome-message">
            <div class="welcome-icon">👋</div>
            <h2>Hello! I'm EVA</h2>
            <p>Your Offline Voice Assistant</p>
            <div class="feature-pills">
                <span class="pill">🎤 Voice Commands</span>
                <span class="pill">⌨️ Text Input</span>
                <span class="pill">🔒 Offline</span>
            </div>
            <p class="hint">Type a message or click the microphone to start...</p>
        </div>
    `;
    showNotification('Cleared', 'Chat history cleared', 'info');
}

// ============================================
// THEME TOGGLE (FIXED)
// ============================================

function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        icon.textContent = '☀️';
        localStorage.setItem('eva-theme', 'light');
        showNotification('Theme', 'Switched to Light Mode', 'info');
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        icon.textContent = '🌙';
        localStorage.setItem('eva-theme', 'dark');
        showNotification('Theme', 'Switched to Dark Mode', 'info');
    }
}

// Load saved theme
function loadTheme() {
    const saved = localStorage.getItem('eva-theme');
    if (saved === 'light') {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
        document.getElementById('theme-icon').textContent = '☀️';
    }
}

// ============================================
// NOTIFICATIONS (FIXED)
// ============================================

function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">${icons[type]}</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    // Click to dismiss
    notification.onclick = () => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => notification.remove(), 300);
    };
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 EVA initialized');
    
    // Load theme
    loadTheme();
    
    // Enter key to send
    const input = document.getElementById('chat-input');
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendTextMessage();
        }
    });
    
    // Focus input
    input.focus();
});