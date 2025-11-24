import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Mic, MicOff, Send, Volume2, VolumeX, 
  Settings, History, Trash2, Download, 
  Power, Minimize, X, User, Bot 
} from 'lucide-react';
import './App.css';

// Backend URL - Change this to match your Python backend
const BACKEND_URL = 'http://localhost:5000';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const chatEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Check backend connection
  useEffect(() => {
    checkConnection();
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setMessage(transcript);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  }, []);

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/health`, { timeout: 3000 });
      setIsConnected(response.status === 200);
    } catch (error) {
      setIsConnected(false);
      console.error('Backend connection failed:', error);
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not supported. Please use Chrome or Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleSubmit = async () => {
    if (!message.trim() || isProcessing) return;

    const userMessage = message.trim();
    setMessage('');
    setIsProcessing(true);

    // Add user message
    setChatHistory(prev => [...prev, { 
      type: 'user', 
      text: userMessage, 
      timestamp: new Date() 
    }]);

    try {
      // Call your Python backend
      const response = await axios.post(`${BACKEND_URL}/query`, {
        query: userMessage
      }, {
        timeout: 30000 // 30 seconds timeout
      });

      const evaResponse = response.data.response || response.data.message || 'No response';
      
      // Add EVA response
      setChatHistory(prev => [...prev, { 
        type: 'eva', 
        text: evaResponse, 
        timestamp: new Date() 
      }]);

      // Speak response
      if (voiceEnabled) {
        speakText(evaResponse);
      }
    } catch (error) {
      console.error('Backend error:', error);
      const errorMsg = error.response?.data?.error || 
                       'Sorry, I encountered an error. Please check if the backend is running.';
      
      setChatHistory(prev => [...prev, { 
        type: 'eva', 
        text: errorMsg, 
        timestamp: new Date() 
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Stop any ongoing speech
      setIsSpeaking(true);
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;
      utterance.lang = 'en-US';
      
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const clearHistory = () => {
    setChatHistory([]);
    setShowHistory(false);
  };

  const exportHistory = () => {
    const content = chatHistory.map(msg => 
      `[${msg.timestamp.toLocaleString()}] ${msg.type.toUpperCase()}: ${msg.text}`
    ).join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eva-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="app">
      {/* Title Bar */}
      <div className="titlebar">
        <div className="titlebar-left">
          <div className="app-icon">E</div>
          <span className="app-title">EVA Desktop Assistant</span>
          <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            <span>{isConnected ? '● Connected' : '● Disconnected'}</span>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="main-container">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="sidebar-header">
            <h2>Menu</h2>
          </div>
          <div className="sidebar-menu">
            <button className="menu-item active">
              <Bot size={20} />
              <span>Chat</span>
            </button>
            <button 
              className="menu-item"
              onClick={() => setShowHistory(true)}
            >
              <History size={20} />
              <span>History</span>
            </button>
            <button 
              className="menu-item"
              onClick={() => setShowSettings(true)}
            >
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-container">
          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="welcome-screen">
                <div className="welcome-icon">
                  <Mic size={64} />
                </div>
                <h1>Hello, I'm EVA</h1>
                <p>Your Offline Desktop Assistant</p>
                <div className="suggestion-cards">
                  <div 
                    className="suggestion-card"
                    onClick={() => setMessage("What can you do?")}
                  >
                    <p>What can you do?</p>
                  </div>
                  <div 
                    className="suggestion-card"
                    onClick={() => setMessage("What's the time?")}
                  >
                    <p>What's the time?</p>
                  </div>
                  <div 
                    className="suggestion-card"
                    onClick={() => setMessage("Open notepad")}
                  >
                    <p>Open notepad</p>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.type}`}>
                    <div className="message-avatar">
                      {msg.type === 'user' ? <User size={20} /> : <Bot size={20} />}
                    </div>
                    <div className="message-content">
                      <div className="message-text">{msg.text}</div>
                      <div className="message-time">
                        {msg.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                {isProcessing && (
                  <div className="message eva">
                    <div className="message-avatar">
                      <Bot size={20} />
                    </div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div className="input-container">
            <button
              className={`mic-button ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              title={isListening ? 'Stop listening' : 'Start listening'}
            >
              {isListening ? <MicOff size={24} /> : <Mic size={24} />}
            </button>
            
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type or speak your command..."
              className="message-input"
              disabled={isProcessing}
            />
            
            {isSpeaking && (
              <button
                className="stop-button"
                onClick={stopSpeaking}
                title="Stop speaking"
              >
                <VolumeX size={24} />
              </button>
            )}
            
            <button
              className="send-button"
              onClick={handleSubmit}
              disabled={!message.trim() || isProcessing}
              title="Send message"
            >
              <Send size={24} />
            </button>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay" onClick={() => setShowSettings(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Settings</h3>
            <div className="settings-content">
              <div className="setting-item">
                <span>Voice Responses</span>
                <button
                  className={`toggle-button ${voiceEnabled ? 'active' : ''}`}
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                >
                  {voiceEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                </button>
              </div>
              <div className="setting-item">
                <span>Backend URL</span>
                <input 
                  type="text" 
                  value={BACKEND_URL} 
                  readOnly 
                  className="url-input"
                />
              </div>
              <button 
                className="reconnect-button"
                onClick={checkConnection}
              >
                Test Connection
              </button>
            </div>
            <button 
              className="close-button"
              onClick={() => setShowSettings(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Chat History</h3>
            {chatHistory.length === 0 ? (
              <p className="empty-message">No chat history yet</p>
            ) : (
              <div className="history-content">
                {chatHistory.map((msg, idx) => (
                  <div key={idx} className="history-item">
                    <span className="history-type">{msg.type.toUpperCase()}</span>
                    <p className="history-text">{msg.text}</p>
                  </div>
                ))}
              </div>
            )}
            <div className="modal-actions">
              <button 
                className="export-button"
                onClick={exportHistory}
                disabled={chatHistory.length === 0}
              >
                <Download size={18} />
                Export
              </button>
              <button 
                className="clear-button"
                onClick={clearHistory}
                disabled={chatHistory.length === 0}
              >
                <Trash2 size={18} />
                Clear
              </button>
            </div>
            <button 
              className="close-button"
              onClick={() => setShowHistory(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;