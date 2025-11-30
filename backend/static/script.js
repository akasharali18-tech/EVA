// Initialize Socket.IO connection
const socket = io();

let isVoiceActive = false;
let voiceResponseEnabled = true;
let autoScrollEnabled = true;
let notificationsEnabled = true;
let currentTheme = 'dark';

// Load saved preferences
loadPreferences();

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to EVA server');
    showNotification('Connected', 'Successfully connected to EVA server', 'success');
});

socket.on('disconnect', () => {
    console.log('Disconnected from EVA server');
    showNotification('Disconnected', 'Lost connection to EVA server', 'error');
    if (isVoiceActive) {
        stopVoiceInput();
    }
});

socket.on('command_received', (data) => {
    addMessage('YOU', data.command, 'user-message');
});

socket.on('response', (data) => {
    addMessage('EVA', data.message, 'bot-message');
});

socket.on('activated', () => {
    updateStatus(true);
    showNotification('Voice Active', 'Say "EVA" to give commands', 'info');
});

socket.on('deactivated', () => {
    updateStatus(false);
    stopVoiceInput();
});

// Notification System
function showNotification(title, message, type = 'info') {
    if (!notificationsEnabled) return;
    
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
    };
    
    notification.innerHTML = `
        <div class="notification-icon">${icons[type] || 'ℹ'}</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    // Click to dismiss
    notification.addEventListener('click', () => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
}

// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        themeIcon.textContent = '☀️';
        currentTheme = 'light';
        darkModeToggle.checked = false;
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        themeIcon.textContent = '🌙';
        currentTheme = 'dark';
        darkModeToggle.checked = true;
    }
    
    savePreferences();
}

// Voice Input Functions
function toggleVoiceInput() {
    if (!isVoiceActive) {
        startVoiceInput();
    } else {
        stopVoiceInput();
    }
}

function startVoiceInput() {
    isVoiceActive = true;
    const voiceBtn = document.getElementById('voice-btn');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    voiceBtn.classList.add('active');
    listeningIndicator.classList.add('active');
    
    socket.emit('activate');
}

function stopVoiceInput() {
    isVoiceActive = false;
    const voiceBtn = document.getElementById('voice-btn');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    voiceBtn.classList.remove('active');
    listeningIndicator.classList.remove('active');
    
    socket.emit('deactivate');
}

// Message Functions
function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (message) {
        // Hide welcome message if it exists
        hideWelcomeMessage();
        
        socket.emit('manual_command', { command: message });
        input.value = '';
        input.focus();
    }
}

function quickCommand(command) {
    hideWelcomeMessage();
    socket.emit('manual_command', { command: command });
}

function updateStatus(active) {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    if (active) {
        statusDot.classList.remove('inactive');
        statusDot.classList.add('active');
        statusText.textContent = 'LISTENING';
    } else {
        statusDot.classList.remove('active');
        statusDot.classList.add('inactive');
        statusText.textContent = 'INACTIVE';
    }
}

function addMessage(sender, text, type) {
    const chatContainer = document.getElementById('chat-container');
    
    // Hide welcome message on first message
    hideWelcomeMessage();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    messageDiv.innerHTML = `
        <span class="message-sender">${sender}:</span>
        <span class="message-text">${text}</span>
    `;
    
    chatContainer.appendChild(messageDiv);
    
    if (autoScrollEnabled) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function hideWelcomeMessage() {
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
}

function clearChat() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = `
        <div class="welcome-message">
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
    showNotification('Chat Cleared', 'Conversation history cleared', 'info');
}

// Settings Functions
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    panel.classList.toggle('open');
}

// Preferences Management
function savePreferences() {
    const prefs = {
        theme: currentTheme,
        voiceResponse: voiceResponseEnabled,
        autoScroll: autoScrollEnabled,
        notifications: notificationsEnabled
    };
    localStorage.setItem('eva_preferences', JSON.stringify(prefs));
}

function loadPreferences() {
    const saved = localStorage.getItem('eva_preferences');
    if (saved) {
        const prefs = JSON.parse(saved);
        
        // Apply theme
        if (prefs.theme === 'light') {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            document.getElementById('theme-icon').textContent = '☀️';
            currentTheme = 'light';
        }
        
        // Apply other preferences
        voiceResponseEnabled = prefs.voiceResponse !== false;
        autoScrollEnabled = prefs.autoScroll !== false;
        notificationsEnabled = prefs.notifications !== false;
        
        // Update toggles
        document.getElementById('voice-response-toggle').checked = voiceResponseEnabled;
        document.getElementById('auto-scroll-toggle').checked = autoScrollEnabled;
        document.getElementById('notifications-toggle').checked = notificationsEnabled;
        document.getElementById('dark-mode-toggle').checked = currentTheme === 'dark';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    
    // Enter key to send
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Settings toggles
    document.getElementById('voice-response-toggle').addEventListener('change', (e) => {
        voiceResponseEnabled = e.target.checked;
        savePreferences();
    });
    
    document.getElementById('auto-scroll-toggle').addEventListener('change', (e) => {
        autoScrollEnabled = e.target.checked;
        savePreferences();
    });
    
    document.getElementById('notifications-toggle').addEventListener('change', (e) => {
        notificationsEnabled = e.target.checked;
        savePreferences();
        showNotification('Settings', `Notifications ${e.target.checked ? 'enabled' : 'disabled'}`, 'info');
    });
    
    // Focus input on load
    chatInput.focus();
});

// Click outside settings to close
document.addEventListener('click', (e) => {
    const panel = document.getElementById('settings-panel');
    const settingsBtn = document.querySelector('.settings-btn');
    
    if (panel.classList.contains('open') && 
        !panel.contains(e.target) && 
        e.target !== settingsBtn &&
        !settingsBtn.contains(e.target)) {
        panel.classList.remove('open');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('chat-input').focus();
    }
    
    // Ctrl/Cmd + L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
    
    // Escape to close settings
    if (e.key === 'Escape') {
        const panel = document.getElementById('settings-panel');
        if (panel.classList.contains('open')) {
            panel.classList.remove('open');
        }
    }
});