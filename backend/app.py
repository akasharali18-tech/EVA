"""
EVA Voice Assistant - Flask Web Server (FIXED VERSION)
This version properly handles voice input and responses
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from ui_bridge import EVABridge

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eva_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize bridge
bridge = EVABridge()
is_listening = False
listen_thread = None

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print("✅ Client connected")
    emit('connected', {'message': 'Connected to EVA server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    global is_listening
    is_listening = False
    print("❌ Client disconnected")

@socketio.on('start_voice')
def handle_start_voice():
    """Start voice listening mode"""
    global is_listening, listen_thread
    
    print("🎤 Starting voice mode...")
    
    if is_listening:
        print("⚠️ Already listening")
        return
    
    is_listening = True
    emit('voice_started', {'status': True})
    
    def voice_listening_loop():
        """Continuously listen for voice commands"""
        global is_listening
        
        while is_listening:
            try:
                print("👂 Listening for speech...")
                socketio.emit('listening_status', {'status': 'listening'})
                
                # Listen for voice input
                command = bridge.listen()
                
                if command and is_listening:
                    print(f"🗣️ Heard: {command}")
                    
                    # Send what user said to frontend
                    socketio.emit('speech_recognized', {'text': command})
                    
                    # Check if it's a wake word
                    if "eva" in command.lower() or "hey eva" in command.lower():
                        socketio.emit('wake_word_detected', {'message': 'Yes, listening...'})
                        
                        # Speak response
                        threading.Thread(
                            target=bridge.speak, 
                            args=("Yes, I'm listening",), 
                            daemon=True
                        ).start()
                        
                        # Wait briefly and listen for actual command
                        time.sleep(0.5)
                        
                        print("👂 Listening for actual command...")
                        actual_command = bridge.listen()
                        
                        if actual_command and is_listening:
                            print(f"🗣️ Command: {actual_command}")
                            socketio.emit('speech_recognized', {'text': actual_command})
                            
                            # Process the command
                            result = bridge.process_command(actual_command)
                            
                            if result:
                                print(f"🤖 Response: {result}")
                                socketio.emit('command_response', {'response': result})
                                
                                # Speak the response
                                threading.Thread(
                                    target=bridge.speak, 
                                    args=(result,), 
                                    daemon=True
                                ).start()
                    
                    else:
                        # Direct command without wake word
                        result = bridge.process_command(command)
                        if result and result != "Sorry, I didn't understand that command. Please try again.":
                            print(f"🤖 Response: {result}")
                            socketio.emit('command_response', {'response': result})
                            threading.Thread(
                                target=bridge.speak, 
                                args=(result,), 
                                daemon=True
                            ).start()
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except Exception as e:
                print(f"❌ Voice loop error: {e}")
                time.sleep(0.5)
        
        print("🛑 Voice listening stopped")
    
    # Start listening in background thread
    listen_thread = threading.Thread(target=voice_listening_loop, daemon=True)
    listen_thread.start()

@socketio.on('stop_voice')
def handle_stop_voice():
    """Stop voice listening mode"""
    global is_listening
    print("🛑 Stopping voice mode...")
    is_listening = False
    emit('voice_stopped', {'status': False})

@socketio.on('send_text_command')
def handle_text_command(data):
    """Handle text command input"""
    try:
        command = data.get('command', '').strip()
        if not command:
            return
        
        print(f"⌨️ Text command: {command}")
        
        # Process command
        result = bridge.process_command(command)
        
        if result:
            print(f"🤖 Response: {result}")
            emit('command_response', {'response': result})
            
            # Speak response in background
            threading.Thread(
                target=bridge.speak, 
                args=(result,), 
                daemon=True
            ).start()
            
    except Exception as e:
        print(f"❌ Text command error: {e}")
        emit('command_response', {'response': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 EVA Voice Assistant - Flask Server (FIXED VERSION)")
    print("=" * 60)
    print("🌐 Open: http://localhost:5000")
    print("🎤 Voice commands fully working")
    print("🌓 Theme toggle working")
    print("🔔 Notifications working")
    print("⚠️  Press Ctrl+C to stop")
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)