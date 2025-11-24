import speech_recognition as sr
import pyttsx3
import datetime
import sys
import webbrowser
import os
import subprocess

# ---------------------------------------------------------
#  TEXT-TO-SPEECH
# ---------------------------------------------------------
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
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    print(f"EVA: {text}")

# ---------------------------------------------------------
#  LISTEN FUNCTION
# ---------------------------------------------------------
def listen():
    recognizer = sr.Recognizer()

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
                print(f"❌ Recognition error: {e}")
                return ""

    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return ""

# ---------------------------------------------------------
#  GREETING
# ---------------------------------------------------------
def greet_user():
    hour = datetime.datetime.now().hour

    if 0 <= hour < 12:
        greet = "Good Morning!"
    elif 12 <= hour < 18:
        greet = "Good Afternoon!"
    else:
        greet = "Good Evening!"

    speak(greet)
    speak("I am EVA, your assistant. How can I help you?")

# ---------------------------------------------------------
#  UNIVERSAL OPEN COMMAND (VERY IMPORTANT)
# ---------------------------------------------------------
def universal_open(query):
    query = query.lower()

    # ---------- OPEN CAMERA ----------
    if "camera" in query:
        from modules.open_camera import open_camera
        return open_camera()

    # ---------- POPULAR WEBSITES ----------
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "flipkart": "https://www.flipkart.com",
        "linkedin": "https://www.linkedin.com",
        "github": "https://github.com",
        "chatgpt": "https://chat.openai.com"
    }

    for name, url in websites.items():
        if name in query:
            webbrowser.open(url)
            return f"Opening {name}"

    # ---------- ANY WEBSITE URL ----------
    if ".com" in query or ".in" in query or ".org" in query:
        url = query.replace("open", "").strip()
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return "Opening website"

    # ---------- WINDOWS APPS ----------
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "control panel": "control.exe"
    }

    for name, exe in apps.items():
        if name in query:
            subprocess.Popen(exe)
            return f"Opening {name}"

    # ---------- FOLDERS ----------
    folders = {
        "downloads": os.path.expanduser("~/Downloads"),
        "documents": os.path.expanduser("~/Documents"),
        "desktop": os.path.expanduser("~/Desktop"),
        "pictures": os.path.expanduser("~/Pictures")
    }

    for name, path in folders.items():
        if name in query:
            os.startfile(path)
            return f"Opening {name} folder"

    return "Sorry, I don't know how to open that."

# ---------------------------------------------------------
#  PROCESS COMMAND
# ---------------------------------------------------------
def process_command(query):
    if not query:
        return True

    try:
        # TIME
        if "time" in query:
            speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))

        # DATE
        elif "date" in query:
            speak("Today's date is " + datetime.datetime.now().strftime("%B %d, %Y"))

        # GREETINGS
        elif "hello" in query or "hi" in query:
            speak("Hello! How can I help you?")

        # UNIVERSAL OPEN COMMAND 🚀
        elif "open" in query:
            speak(universal_open(query))

        # CAPTURE PHOTO
        elif "capture photo" in query or "take photo" in query:
            from modules.open_camera import capture_photo
            speak("Capturing photo...")
            speak(capture_photo())

        # RECORD VIDEO
        elif "record video" in query:
            from modules.open_camera import record_video
            speak("Recording video for five seconds...")
            speak(record_video(5))

        # SWITCH CAMERA
        elif "switch camera" in query:
            from modules.open_camera import switch_camera, open_camera
            new_cam = switch_camera(0)
            speak("Switching camera")
            speak(open_camera(new_cam))

        # EXIT
        elif "bye" in query or "quit" in query or "exit" in query:
            speak("Goodbye! Have a great day!")
            return False

        else:
            speak(f"You said: {query}. I am still learning that command.")

        return True

    except Exception as e:
        print(f"Command error: {e}")
        speak("Sorry, I encountered an error.")
        return True

# ---------------------------------------------------------
#  MAIN
# ---------------------------------------------------------
def main():
    print("=" * 60)
    print("          EVA - Enhanced Voice Assistant")
    print("=" * 60)

    greet_user()

    while True:
        query = listen()
        if query:
            if not process_command(query):
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEVA shutting down...")
        speak("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
