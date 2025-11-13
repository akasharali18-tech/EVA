import speech_recognition as sr
import pyttsx3
import datetime
import os
import sys
import types

# Patch missing 'aifc' for Python 3.13+
if 'aifc' not in sys.modules:
    sys.modules['aifc'] = types.ModuleType('aifc')

# Add modules folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.command_handler import handle_command
from modules.get_time_date import get_time, get_date

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Configure voice settings
def configure_voice():
    """Configure TTS engine properties"""
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # 0=Male, 1=Female
    engine.setProperty('rate', 175)  # Speed of speech
    engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

configure_voice()

def speak(text):
    """Convert text to speech"""
    print(f"🗣️  EVA: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to user voice and convert to text"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎧 Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=5)
            print("🔄 Recognizing...")
            
            # Using Google Speech Recognition (works offline with cache)
            # For fully offline, use Vosk (see alternative below)
            query = recognizer.recognize_google(audio, language='en-US')
            print(f"🗣️  You said: {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            return "none"
        except sr.UnknownValueError:
            return "none"
        except sr.RequestError:
            speak("Speech recognition service is unavailable")
            return "none"
        except Exception as e:
            print(f"Error: {e}")
            return "none"

def wish_user():
    """Greet user based on time of day"""
    hour = datetime.datetime.now().hour
    
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    
    speak("I am EVA, your offline voice assistant. How can I help you today?")

def main():
    """Main function to run EVA"""
    wish_user()
    
    while True:
        # Listen for wake word
        query = listen()
        
        if query == "none":
            continue
        
        # Check for wake word "eva"
        if "eva" in query or "hey eva" in query or "ok eva" in query:
            speak("Yes, I'm listening. What can I do for you?")
            
            # Listen for actual command
            command = listen()
            
            if command != "none":
                # Handle the command
                result = handle_command(command)
                
                if result == "exit":
                    speak("Goodbye! Have a great day!")
                    break
                elif result:
                    speak(result)

if __name__ == "__main__":
    main()