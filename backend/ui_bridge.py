"""
UI Bridge - Connects Frontend to Backend (FIXED)
"""
import threading
import speech_recognition as sr
import pyttsx3
from modules.command_handler import handle_command
from modules.get_time_date import get_time, get_date

class EVABridge:
    """Bridge between Web UI and EVA backend"""
    
    def __init__(self):
        print("🔧 Initializing EVA Bridge...")
        
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            self.configure_voice()
            print("✅ TTS Engine initialized")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            self.engine = None
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust for sensitivity
        self.recognizer.dynamic_energy_threshold = True
        print("✅ Speech Recognizer initialized")
    
    def configure_voice(self):
        """Configure TTS settings"""
        try:
            if self.engine:
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)  # Female
                self.engine.setProperty('rate', 175)
                self.engine.setProperty('volume', 1.0)
        except Exception as e:
            print(f"Voice config error: {e}")
    
    def speak(self, text):
        """Text to speech"""
        try:
            if self.engine:
                print(f"🔊 Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"Speak error: {e}")
    
    def listen(self):
        """Listen for voice input - FIXED VERSION"""
        try:
            with sr.Microphone() as source:
                print("🎤 Microphone active...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                print("👂 Listening for speech...")
                
                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                print("🔄 Processing speech...")
                
                # Recognize speech using Google
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    print(f"✅ Recognized: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    print("⚠️ Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    return None
                
        except sr.WaitTimeoutError:
            print("⏱️ Listening timeout")
            return None
        except Exception as e:
            print(f"❌ Listen error: {e}")
            return None
    
    def process_command(self, command):
        """Process command through backend"""
        try:
            print(f"⚙️ Processing: {command}")
            result = handle_command(command)
            print(f"✅ Result: {result}")
            return result
        except Exception as e:
            print(f"❌ Command error: {e}")
            return f"Error: {str(e)}"