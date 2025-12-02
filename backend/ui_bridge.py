# ==========================================
# FILE 1: backend/ui_bridge.py (FIXED VERSION)
# ==========================================
"""
UI Bridge - Connects Flask Web UI to EVA backend
FIXED: Better error handling, improved listening, proper threading
"""
import threading
import queue
from modules.command_handler import handle_command
import speech_recognition as sr
import pyttsx3
import time

class EVABridge:
    """Bridge between Web UI and EVA backend"""
    
    def __init__(self):
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.configure_voice()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        # Adjust recognizer sensitivity
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Status flags
        self.is_listening = False
        self.is_active = False
        self.is_speaking = False
        
        # Thread lock for TTS
        self.speak_lock = threading.Lock()
    
    def configure_voice(self):
        """Configure TTS settings"""
        try:
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Female voice
            else:
                self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"Voice configuration error: {e}")
    
    def speak(self, text):
        """Text to speech with thread safety"""
        if not text:
            return
        
        with self.speak_lock:
            try:
                self.is_speaking = True
                print(f"[TTS] Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            except Exception as e:
                print(f"Speak error: {e}")
                self.is_speaking = False
    
    def listen(self):
        """
        Listen for voice input with improved error handling
        Returns the recognized text or None
        """
        try:
            with sr.Microphone() as source:
                print("[MIC] Adjusting for ambient noise...")
                # Quick noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                print("[MIC] Listening...")
                # Listen with longer timeout and phrase limit
                audio = self.recognizer.listen(
                    source, 
                    timeout=10,  # Increased timeout
                    phrase_time_limit=10  # Increased phrase limit
                )
                
                print("[MIC] Processing audio...")
                # Try to recognize
                query = self.recognizer.recognize_google(audio, language='en-US')
                print(f"[MIC] Recognized: {query}")
                return query.lower()
                
        except sr.WaitTimeoutError:
            print("[MIC] Timeout - No speech detected")
            return None
        except sr.UnknownValueError:
            print("[MIC] Could not understand audio")
            return "sorry i could not understand"
        except sr.RequestError as e:
            print(f"[MIC] Recognition service error: {e}")
            return None
        except Exception as e:
            print(f"[MIC] Listen error: {e}")
            return None
    
    def process_command(self, command):
        """Process command through backend"""
        if not command:
            return "I didn't catch that. Please try again."
        
        try:
            print(f"[PROCESS] Command: {command}")
            result = handle_command(command)
            print(f"[PROCESS] Result: {result}")
            return result if result else "Command processed."
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(f"[PROCESS] {error_msg}")
            return error_msg
    
    def stop_listening(self):
        """Stop listening thread"""
        self.is_listening = False
        print("[BRIDGE] Stopped listening")

