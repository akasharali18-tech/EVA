import speech_recognition as sr
import pyttsx3
import datetime
import sys

# Initialize text-to-speech
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)
except Exception as e:
    print(f"Warning: TTS initialization issue: {e}")
    engine = None

def speak(text):
    """Convert text to speech"""
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    print(f"EVA: {text}")

def listen():
    """Listen using sounddevice backend (No PyAudio needed!)"""
    recognizer = sr.Recognizer()
    
    # Use sounddevice as microphone backend
    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening... (Speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.pause_threshold = 1
            
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🔍 Recognizing...")
                query = recognizer.recognize_google(audio, language='en-US')
                print(f"✓ You said: {query}\n")
                return query.lower()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"❌ Recognition service error: {e}")
                return ""
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if microphone is connected")
        print("2. Grant microphone permissions to Python")
        print("3. Try: pip install --upgrade sounddevice")
        return ""

def greet_user():
    """Greet based on time"""
    hour = datetime.datetime.now().hour
    
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"
    
    speak(greeting)
    speak("I am EVA, your voice assistant. How can I help you?")

def process_command(query):
    """Process user commands"""
    if not query:
        return True
    
    try:
        if 'time' in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}")
        
        elif 'date' in query:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today is {current_date}")
        
        elif 'hello' in query or 'hi' in query:
            speak("Hello! How can I assist you?")
        
        elif 'how are you' in query:
            speak("I'm doing great, thank you for asking!")
        
        elif 'your name' in query or 'who are you' in query:
            speak("I am EVA, your Enhanced Voice Assistant")
        
        elif 'quit' in query or 'exit' in query or 'bye' in query or 'goodbye' in query:
            speak("Goodbye! Have a wonderful day!")
            return False
            # ----- OPEN ANY WEBSITE -----
        
        elif "open youtube" in query:
            from modules.open_website import open_website
            speak(open_website("youtube.com", "YouTube"))
        
        elif "open google" in query:
            from modules.open_website import open_website
            speak(open_website("google.com", "Google"))

        elif "open instagram" in query:
            from modules.open_website import open_website
            speak(open_website("instagram.com", "Instagram"))

        elif "open linkedin" in query:
            from modules.open_website import open_website
            speak(open_website("in.linkedin.com", "linkedin"))
        
        elif "open flipkart" in query:
            from modules.open_website import open_website
            speak(open_website("flipkart.com", "flipkart"))
        
        elif "open camera" in query:
            from modules.open_camera import open_camera
            speak("Opening camera")
            speak(open_camera())

        elif "capture photo" in query or "take photo" in query:
            from modules.open_camera import capture_photo
            speak("Capturing photo")
            speak(capture_photo())
        
        # ----- RECORD VIDEO -----
        elif "record video" in query:
            from modules.open_camera import record_video
            speak("Recording video for five seconds")
            speak(record_video(5))
        # ----- SWITCH CAMERA -----
        elif "switch camera" in query:
            from modules.open_camera import switch_camera, open_camera
            camera_id = switch_camera(0)  # simple example
            speak("Switching camera")
            speak(open_camera(camera_id))
        
        else:
            speak(f"You said: {query}. I'm still learning to handle this command.")
        
        return True
    
    except Exception as e:
        print(f"Command processing error: {e}")
        speak("Sorry, I encountered an error")
        return True

def main():
    """Main EVA function"""
    print("=" * 60)
    print("          EVA - Enhanced Voice Assistant (Python 3.14)")
    print("=" * 60)
    print("\nInitializing...")
    
    # Test microphone availability
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"✓ Found {len(devices)} audio devices")
    except Exception as e:
        print(f"⚠ Warning: Could not query audio devices: {e}")
    
    greet_user()
    print("\n💡 Try saying: 'What time is it?' or 'Hello' or 'Goodbye'\n")
    
    while True:
        query = listen()
        if query:
            if not process_command(query):
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 EVA shutting down...")
        speak("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)