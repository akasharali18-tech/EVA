"""
UI Bridge - Connects Flask Web UI to EVA backend
"""
import threading
import queue
from modules.command_handler import handle_command
from modules.get_time_date import get_time, get_date
import speech_recognition as sr
import pyttsx3

class EVABridge:
    """Bridge between Web UI and EVA backend"""
    
    def __init__(self):
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.configure_voice()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Status flags
        self.is_listening = False
        self.is_active = False
    
    def configure_voice(self):
        """Configure TTS settings"""
        try:
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Female voice
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"Voice configuration error: {e}")
    
    def speak(self, text):
        """Text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speak error: {e}")
    
    def listen(self):
        """Listen for voice input"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                query = self.recognizer.recognize_google(audio, language='en-US')
                return query.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"Listen error: {e}")
            return None
    
    def process_command(self, command):
        """Process command through backend"""
        try:
            result = handle_command(command)
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stop_listening(self):
        """Stop listening thread"""
        self.is_listening = False