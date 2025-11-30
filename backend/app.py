"""
EVA Voice Assistant - Flask Web Server
Run this file for Option 2 (Web UI)
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from ui_bridge import EVABridge


app = Flask(__name__)
app.config['SECRET_KEY'] = 'eva_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

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
    print("Client connected")
    emit('status', {'message': 'Connected to EVA server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    global is_listening
    is_listening = False
    print("Client disconnected")

@socketio.on('activate')
def handle_activate():
    """Activate EVA listening"""
    global is_listening, listen_thread
    
    if is_listening:
        return
    
    is_listening = True
    
    def listen_loop():
        global is_listening
        socketio.emit('activated', {'status': True})
        
        while is_listening:
            try:
                command = bridge.listen()
                if command and is_listening:
                    socketio.emit('command_received', {'command': command})
                    
                    # Check for wake word
                    if "eva" in command or "hey eva" in command:
                        socketio.emit('response', {'message': 'Yes, I\'m listening...'})
                        
                        # Use threading to speak without blocking
                        threading.Thread(target=bridge.speak, args=("Yes, I'm listening",), daemon=True).start()
                        
                        # Wait a moment then listen for actual command
                        time.sleep(0.5)
                        actual_command = bridge.listen()
                        
                        if actual_command and is_listening:
                            socketio.emit('command_received', {'command': actual_command})
                            result = bridge.process_command(actual_command)
                            
                            if result == "exit":
                                socketio.emit('response', {'message': 'Goodbye!'})
                                threading.Thread(target=bridge.speak, args=("Goodbye!",), daemon=True).start()
                                is_listening = False
                                socketio.emit('deactivated', {'status': False})
                            elif result:
                                socketio.emit('response', {'message': result})
                                threading.Thread(target=bridge.speak, args=(result,), daemon=True).start()
                
            except Exception as e:
                print(f"Listen loop error: {e}")
                time.sleep(0.5)
    
    listen_thread = threading.Thread(target=listen_loop, daemon=True)
    listen_thread.start()

@socketio.on('deactivate')
def handle_deactivate():
    """Deactivate EVA"""
    global is_listening
    is_listening = False
    emit('deactivated', {'status': False})

@socketio.on('manual_command')
def handle_manual_command(data):
    """Handle manual command input"""
    try:
        command = data.get('command', '').strip()
        if not command:
            return
        
        emit('command_received', {'command': command})
        result = bridge.process_command(command)
        
        if result == "exit":
            emit('response', {'message': 'Goodbye!'})
            threading.Thread(target=bridge.speak, args=("Goodbye!",), daemon=True).start()
        elif result:
            emit('response', {'message': result})
            threading.Thread(target=bridge.speak, args=(result,), daemon=True).start()
        else:
            emit('response', {'message': 'Command executed'})
            
    except Exception as e:
        emit('response', {'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 EVA Voice Assistant - Flask Server")
    print("=" * 50)
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🎤 Make sure your microphone is connected")
    print("⚠️  Press Ctrl+C to stop the server")
    print("=" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)