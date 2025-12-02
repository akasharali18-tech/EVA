# ==========================================
# FILE 2: backend/app.py (FIXED VERSION)
# ==========================================
"""
EVA Voice Assistant - Flask Web Server
FIXED: Better socket handling, improved threading, proper command flow
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
    print("=" * 50)
    print("✅ Client connected")
    print("=" * 50)
    emit('status', {'message': 'Connected to EVA server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    global is_listening
    is_listening = False
    print("❌ Client disconnected")

@socketio.on('activate')
def handle_activate():
    """Activate EVA listening"""
    global is_listening, listen_thread
    
    if is_listening:
        print("⚠️ Already listening")
        return
    
    is_listening = True
    print("🎤 Voice activation requested")
    
    def listen_loop():
        global is_listening
        
        # Notify frontend that we're active
        socketio.emit('activated', {'status': True})
        socketio.emit('response', {'message': 'Voice mode activated. Listening for commands...'})
        
        print("🔊 Listen loop started")
        
        while is_listening:
            try:
                print("\n" + "=" * 50)
                print("👂 Waiting for voice input...")
                print("=" * 50)
                
                # Listen for command
                command = bridge.listen()
                
                if command and is_listening:
                    print(f"✅ Command received: {command}")
                    
                    # Send command to frontend immediately
                    socketio.emit('command_received', {'command': command})
                    
                    # Small delay to show the command in UI
                    time.sleep(0.3)
                    
                    # Process the command
                    print(f"⚙️ Processing: {command}")
                    result = bridge.process_command(command)
                    
                    if result:
                        print(f"📤 Response: {result}")
                        
                        # Check for exit command
                        if result == "exit":
                            socketio.emit('response', {'message': 'Goodbye! Voice mode deactivated.'})
                            threading.Thread(
                                target=bridge.speak, 
                                args=("Goodbye!",), 
                                daemon=True
                            ).start()
                            is_listening = False
                            socketio.emit('deactivated', {'status': False})
                            break
                        else:
                            # Send response to frontend
                            socketio.emit('response', {'message': result})
                            
                            # Speak response in background
                            threading.Thread(
                                target=bridge.speak, 
                                args=(result,), 
                                daemon=True
                            ).start()
                    
                    # Brief pause before next listen
                    time.sleep(0.5)
                
                elif command is None:
                    # Timeout or no speech - continue listening
                    print("⏳ No speech detected, continuing...")
                    time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ Listen loop error: {e}")
                socketio.emit('response', {'message': f'Error: {str(e)}'})
                time.sleep(1)
        
        print("🛑 Listen loop ended")
        socketio.emit('deactivated', {'status': False})
    
    # Start listening in separate thread
    listen_thread = threading.Thread(target=listen_loop, daemon=True)
    listen_thread.start()
    print("✅ Listen thread started")

@socketio.on('deactivate')
def handle_deactivate():
    """Deactivate EVA"""
    global is_listening
    print("🛑 Deactivation requested")
    is_listening = False
    emit('deactivated', {'status': False})
    emit('response', {'message': 'Voice mode deactivated.'})

@socketio.on('manual_command')
def handle_manual_command(data):
    """Handle manual command input (text)"""
    try:
        command = data.get('command', '').strip()
        if not command:
            return
        
        print(f"⌨️ Manual command: {command}")
        print("⏳ No speech detected or not understood, continuing...")
        
        # Echo command to frontend
        emit('command_received', {'command': command})
        
        # Process command
        result = bridge.process_command(command)
        
        if result == "exit":
            emit('response', {'message': 'Goodbye!'})
            threading.Thread(
                target=bridge.speak, 
                args=("Goodbye!",), 
                daemon=True
            ).start()
        elif result:
            emit('response', {'message': result})
            threading.Thread(
                target=bridge.speak, 
                args=(result,), 
                daemon=True
            ).start()
        else:
            emit('response', {'message': 'Command executed successfully.'})
            
    except Exception as e:
        print(f"❌ Manual command error: {e}")
        emit('response', {'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 EVA Voice Assistant - Flask Server")
    print("=" * 60)
    print("🌐 Server URL: http://localhost:5000")
    print("🎤 Make sure your microphone is connected and working")
    print("💡 Click the microphone button to activate voice mode")
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    socketio.run(
        app, 
        debug=False,  # Set to False for better threading
        host='0.0.0.0', 
        port=5000,
        use_reloader=False  # Disable reloader for better stability
    )