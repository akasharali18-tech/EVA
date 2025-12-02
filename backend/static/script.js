// ==========================================
// FILE: backend/static/script.js (FIXED VERSION)
// FIXED: Better event handling, improved UI updates, proper status management
// ==========================================

// Initialize Socket.IO connection
const socket = io();

let isVoiceActive = false;
let voiceResponseEnabled = true;
let autoScrollEnabled = true;
let notificationsEnabled = true;
let currentTheme = 'dark';

// Load saved preferences on startup
loadPreferences();

// ==========================================
// SOCKET EVENT HANDLERS
// ==========================================

socket.on('connect', () => {
    console.log('✅ Connected to EVA server');
    showNotification('Connected', 'Successfully connected to EVA server', 'success');
    addSystemMessage('System connected. Ready to assist!');
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from EVA server');
    showNotification('Disconnected', 'Lost connection to EVA server', 'error');
    addSystemMessage('Disconnected from server. Attempting to reconnect...');
    if (isVoiceActive) {
        stopVoiceInput();
    }
});

socket.on('command_received', (data) => {
    console.log('📥 Command received:', data.command);
    addMessage('YOU', data.command, 'user-message');
});

socket.on('response', (data) => {
    console.log('📤 Response received:', data.message);
    addMessage('EVA', data.message, 'bot-message');
});

socket.on('activated', () => {
    console.log('🎤 Voice mode activated');
    updateStatus(true);
});

socket.on('deactivated', () => {
    console.log('🛑 Voice mode deactivated (from server)');
    
    // Just update local state & UI, do NOT emit again
    isVoiceActive = false;
    
    const voiceBtn = document.getElementById('voice-btn');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    if (voiceBtn) voiceBtn.classList.remove('active');
    if (listeningIndicator) listeningIndicator.classList.remove('active');
    
    updateStatus(false);
});


socket.on('error', (error) => {
    console.error('❌ Socket error:', error);
    showNotification('Error', 'An error occurred. Please try again.', 'error');
});

// ==========================================
// NOTIFICATION SYSTEM
// ==========================================

function showNotification(title, message, type = 'info') {
    if (!notificationsEnabled) return;
    
    const container = document.getElementById('notification-container') || createNotificationContainer();
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
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
    
    // Click to dismiss
    notification.addEventListener('click', () => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
    `;
    document.body.appendChild(container);
    return container;
}

// ==========================================
// VOICE INPUT FUNCTIONS
// ==========================================

function toggleVoiceInput() {
    console.log('🎤 Toggle voice input. Current state:', isVoiceActive);
    if (!isVoiceActive) {
        startVoiceInput();
    } else {
        stopVoiceInput();
    }
}

function startVoiceInput() {
    console.log('▶️ Starting voice input...');
    isVoiceActive = true;
    const voiceBtn = document.getElementById('voice-btn');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    voiceBtn.classList.add('active');
    listeningIndicator.classList.add('active');
    
    // Emit activate event to backend
    socket.emit('activate');
    
    showNotification('Voice Active', 'Speak your command now', 'info');
}

// function stopVoiceInput() {
//     console.log('⏹️ Stopping voice input...');
//     isVoiceActive = false;
//     const voiceBtn = document.getElementById('voice-btn');
//     const listeningIndicator = document.getElementById('listening-indicator');
    
//     voiceBtn.classList.remove('active');
//     listeningIndicator.classList.remove('active');
    
//     // Emit deactivate event to backend
//     socket.emit('deactivate');
// }
function stopVoiceInput() {
    console.log('⏹️ Stopping voice input (user request)...');
    isVoiceActive = false;
    const voiceBtn = document.getElementById('voice-btn');
    const listeningIndicator = document.getElementById('listening-indicator');
    
    if (voiceBtn) voiceBtn.classList.remove('active');
    if (listeningIndicator) listeningIndicator.classList.remove('active');
    
    // This should only be called from user actions / disconnect,
    // NOT from the 'deactivated' socket event.
    socket.emit('deactivate');
}

// ==========================================
// MESSAGE FUNCTIONS
// ==========================================

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (message) {
        console.log('📤 Sending message:', message);
        hideWelcomeMessage();
        
        // Send to backend
        socket.emit('manual_command', { command: message });
        
        // Clear input
        input.value = '';
        input.focus();
    }
}

function quickCommand(command) {
    console.log('⚡ Quick command:', command);
    hideWelcomeMessage();
    socket.emit('manual_command', { command: command });
}

function addMessage(sender, text, type) {
    const chatContainer = document.getElementById('chat-container');
    
    // Hide welcome message on first message
    hideWelcomeMessage();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const timestamp = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div>
            <span class="message-sender">${sender}</span>
            <span class="message-time" style="font-size: 10px; color: #888; margin-left: 8px;">${timestamp}</span>
        </div>
        <span class="message-text">${text}</span>
    `;
    
    chatContainer.appendChild(messageDiv);
    
    if (autoScrollEnabled) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add animation
    messageDiv.style.animation = 'slideIn 0.3s ease';
}

function addSystemMessage(text) {
    const chatContainer = document.getElementById('chat-container');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    
    messageDiv.innerHTML = `
        <span class="message-text">ℹ️ ${text}</span>
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

// ==========================================
// STATUS FUNCTIONS
// ==========================================

function updateStatus(active) {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    console.log('📊 Updating status. Active:', active);
    
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

// ==========================================
// THEME FUNCTIONS
// ==========================================

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

// ==========================================
// SETTINGS FUNCTIONS
// ==========================================

function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    panel.classList.toggle('open');
}

function savePreferences() {
    const prefs = {
        theme: currentTheme,
        voiceResponse: voiceResponseEnabled,
        autoScroll: autoScrollEnabled,
        notifications: notificationsEnabled
    };
    localStorage.setItem('eva_preferences', JSON.stringify(prefs));
    console.log('💾 Preferences saved:', prefs);
}

function loadPreferences() {
    const saved = localStorage.getItem('eva_preferences');
    if (saved) {
        const prefs = JSON.parse(saved);
        console.log('📂 Loading preferences:', prefs);
        
        // Apply theme
        if (prefs.theme === 'light') {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            const themeIcon = document.getElementById('theme-icon');
            if (themeIcon) themeIcon.textContent = '☀️';
            currentTheme = 'light';
        }
        
        // Apply other preferences
        voiceResponseEnabled = prefs.voiceResponse !== false;
        autoScrollEnabled = prefs.autoScroll !== false;
        notificationsEnabled = prefs.notifications !== false;
        
        // Update toggles when DOM is ready
        setTimeout(() => {
            const voiceToggle = document.getElementById('voice-response-toggle');
            const scrollToggle = document.getElementById('auto-scroll-toggle');
            const notifToggle = document.getElementById('notifications-toggle');
            const darkToggle = document.getElementById('dark-mode-toggle');
            
            if (voiceToggle) voiceToggle.checked = voiceResponseEnabled;
            if (scrollToggle) scrollToggle.checked = autoScrollEnabled;
            if (notifToggle) notifToggle.checked = notificationsEnabled;
            if (darkToggle) darkToggle.checked = currentTheme === 'dark';
        }, 100);
    }
}

// ==========================================
// EVENT LISTENERS
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 EVA Frontend initialized');
    
    const chatInput = document.getElementById('chat-input');
    
    // Enter key to send
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Focus input on load
        chatInput.focus();
    }
    
    // Settings toggles
    const voiceToggle = document.getElementById('voice-response-toggle');
    const scrollToggle = document.getElementById('auto-scroll-toggle');
    const notifToggle = document.getElementById('notifications-toggle');
    
    if (voiceToggle) {
        voiceToggle.addEventListener('change', (e) => {
            voiceResponseEnabled = e.target.checked;
            savePreferences();
        });
    }
    
    if (scrollToggle) {
        scrollToggle.addEventListener('change', (e) => {
            autoScrollEnabled = e.target.checked;
            savePreferences();
        });
    }
    
    if (notifToggle) {
        notifToggle.addEventListener('change', (e) => {
            notificationsEnabled = e.target.checked;
            savePreferences();
            showNotification('Settings', `Notifications ${e.target.checked ? 'enabled' : 'disabled'}`, 'info');
        });
    }
});

// Click outside settings to close
document.addEventListener('click', (e) => {
    const panel = document.getElementById('settings-panel');
    const settingsBtn = document.querySelector('.settings-btn');
    
    if (panel && panel.classList.contains('open') && 
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
        document.getElementById('chat-input')?.focus();
    }
    
    // Ctrl/Cmd + L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
    
    // Escape to close settings or stop voice
    if (e.key === 'Escape') {
        const panel = document.getElementById('settings-panel');
        if (panel && panel.classList.contains('open')) {
            panel.classList.remove('open');
        } else if (isVoiceActive) {
            stopVoiceInput();
        }
    }
    
    // Space to toggle voice (when not typing)
    if (e.code === 'Space' && document.activeElement !== document.getElementById('chat-input')) {
        e.preventDefault();
        toggleVoiceInput();
    }
});

console.log('✅ EVA Frontend script loaded successfully')