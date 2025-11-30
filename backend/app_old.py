# ==========================================
# EVA Backend - Flask API Server
# File: backend/app.py
# ==========================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import datetime
import pyttsx3
import speech_recognition as sr
import webbrowser
import wikipedia
import wolframalpha
import requests
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron app

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Female voice: voices[1].id

# Wolframalpha API (Get free API key from https://developer.wolframalpha.com/)
WOLFRAM_API_KEY = "YOUR_WOLFRAM_API_KEY"  # Replace with your API key


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()


def get_time():
    """Get current time"""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")


def get_date():
    """Get current date"""
    now = datetime.datetime.now()
    return now.strftime("%B %d, %Y")


def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except Exception as e:
        return "I couldn't find that on Wikipedia."


def open_application(app_name):
    """Open applications on Windows"""
    apps = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'explorer': 'explorer.exe',
        'word': 'WINWORD.EXE',
        'excel': 'EXCEL.EXE',
        'powerpoint': 'POWERPNT.EXE',
        'paint': 'mspaint.exe',
        'cmd': 'cmd.exe',
    }
    
    try:
        if app_name.lower() in apps:
            subprocess.Popen(apps[app_name.lower()])
            return f"Opening {app_name}"
        else:
            return f"I don't know how to open {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"


def open_website(url):
    """Open website in browser"""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return f"Opening {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"


def search_google(query):
    """Search on Google"""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for {query}"
    except Exception as e:
        return f"Error searching: {str(e)}"


def calculate(expression):
    """Calculate mathematical expressions using Wolframalpha"""
    try:
        if WOLFRAM_API_KEY != "YOUR_WOLFRAM_API_KEY":
            client = wolframalpha.Client(WOLFRAM_API_KEY)
            res = client.query(expression)
            answer = next(res.results).text
            return answer
        else:
            # Fallback to eval for simple calculations
            result = eval(expression)
            return str(result)
    except Exception as e:
        return "I couldn't calculate that."


def get_weather(city=""):
    """Get weather information (requires OpenWeatherMap API)"""
    # You can add OpenWeatherMap API integration here
    return "Weather feature requires API key configuration."


def process_command(command):
    """Process voice/text commands and return appropriate response"""
    command = command.lower()
    
    # Greetings
    if any(word in command for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm EVA, your desktop assistant. How can I help you?"
    
    # Time
    elif 'time' in command:
        current_time = get_time()
        return f"The current time is {current_time}"
    
    # Date
    elif 'date' in command:
        current_date = get_date()
        return f"Today is {current_date}"
    
    # Wikipedia search
    elif 'wikipedia' in command or 'wiki' in command:
        query = command.replace('wikipedia', '').replace('wiki', '').strip()
        result = search_wikipedia(query)
        return result
    
    # Open applications
    elif 'open' in command:
        app_name = command.replace('open', '').strip()
        result = open_application(app_name)
        return result
    
    # Search Google
    elif 'search' in command or 'google' in command:
        query = command.replace('search', '').replace('google', '').strip()
        result = search_google(query)
        return result
    
    # Open website
    elif 'website' in command or '.com' in command or '.org' in command:
        url = command.replace('open website', '').replace('website', '').strip()
        result = open_website(url)
        return result
    
    # Calculate
    elif any(word in command for word in ['calculate', 'what is', 'solve']):
        expression = command.replace('calculate', '').replace('what is', '').replace('solve', '').strip()
        result = calculate(expression)
        return result
    
    # Weather
    elif 'weather' in command:
        result = get_weather()
        return result
    
    # Shutdown/Exit
    elif any(word in command for word in ['shutdown', 'exit', 'quit', 'goodbye', 'bye']):
        return "Goodbye! Have a great day!"
    
    # Help/Capabilities
    elif 'help' in command or 'what can you do' in command:
        return """I can help you with:
        - Tell time and date
        - Search Wikipedia
        - Open applications (notepad, calculator, chrome, etc.)
        - Search Google
        - Open websites
        - Basic calculations
        - And much more! Just ask me."""
    
    # About EVA
    elif 'who are you' in command or 'about' in command:
        return "I'm EVA, an offline desktop voice assistant built with Python and React. I can help you with various tasks on your computer."
    
    # Default response
    else:
        return "I'm not sure how to help with that. Try asking me about the time, opening applications, or searching for something."


# ==========================================
# API ENDPOINTS
# ==========================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'EVA backend is running'
    }), 200


@app.route('/query', methods=['POST'])
def handle_query():
    """Handle text/voice queries from frontend"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'error': 'No query provided'
            }), 400
        
        # Process the command
        response = process_command(query)
        
        return jsonify({
            'response': response,
            'query': query,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({
                'error': 'No text provided'
            }), 400
        
        speak(text)
        
        return jsonify({
            'message': 'Speech completed'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/commands', methods=['GET'])
def get_commands():
    """Get list of available commands"""
    commands = [
        {
            'category': 'General',
            'commands': [
                'Hello / Hi / Hey',
                'What can you do?',
                'Who are you?',
                'Help'
            ]
        },
        {
            'category': 'Time & Date',
            'commands': [
                'What time is it?',
                'What\'s the date today?'
            ]
        },
        {
            'category': 'Applications',
            'commands': [
                'Open notepad',
                'Open calculator',
                'Open chrome',
                'Open explorer'
            ]
        },
        {
            'category': 'Search',
            'commands': [
                'Search [query] on Wikipedia',
                'Google [query]',
                'Open website [url]'
            ]
        },
        {
            'category': 'Calculations',
            'commands': [
                'Calculate [expression]',
                'What is 2 + 2?'
            ]
        }
    ]
    
    return jsonify({
        'commands': commands
    }), 200


# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    print("=" * 50)
    print("EVA Backend Server Starting...")
    print("=" * 50)
    print("Server running on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )