"""
EVA Voice Assistant - Flask Web Server
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
from ui_bridge import EVABridge

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eva_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize bridge
bridge = EVABridge()
is_listening = False

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to EVA server'})

@socketio.on('activate')
def handle_activate():
    """Activate EVA listening"""
    global is_listening
    is_listening = True
    
    def listen_loop():
        while is_listening:
            command = bridge.listen()
            if command:
                socketio.emit('command_received', {'command': command})
                
                if "eva" in command:
                    socketio.emit('response', {'message': 'Yes, listening...'})
                    bridge.speak("Yes, listening")
                    
                    actual_command = bridge.listen()
                    if actual_command:
                        socketio.emit('command_received', {'command': actual_command})
                        result = bridge.process_command(actual_command)
                        
                        if result:
                            socketio.emit('response', {'message': result})
                            bridge.speak(result)
    
    thread = threading.Thread(target=listen_loop, daemon=True)
    thread.start()
    
    emit('activated', {'status': True})

@socketio.on('deactivate')
def handle_deactivate():
    """Deactivate EVA"""
    global is_listening
    is_listening = False
    emit('deactivated', {'status': False})

@socketio.on('manual_command')
def handle_manual_command(data):
    """Handle manual command input"""
    command = data.get('command', '')
    result = bridge.process_command(command)
    
    emit('command_received', {'command': command})
    emit('response', {'message': result or 'Command executed'})
    
    if result:
        bridge.speak(result)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)