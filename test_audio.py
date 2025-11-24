import aifc

with aifc.open("audio.aiff", "rb") as f:
    print(f.getparams())


print("Testing EVA Audio Setup (Python 3.14)...\n")

# Test 1: sounddevice
try:
    import sounddevice as sd
    print("✓ sounddevice installed")
    devices = sd.query_devices()
    print(f"  Found {len(devices)} audio devices")
except Exception as e:
    print(f"✗ sounddevice error: {e}")
 
# Test 2: SpeechRecognition
try:
    import speech_recognition as sr
    print("✓ SpeechRecognition installed")
except Exception as e:
    print(f"✗ SpeechRecognition error: {e}")

# Test 3: pyttsx3
try:
    import pyttsx3
    engine = pyttsx3.init()
    print("✓ pyttsx3 working")
    engine.say("Test")
    engine.runAndWait()
except Exception as e:
    print(f"✗ pyttsx3 error: {e}")

# Test 4: Microphone
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("✓ Microphone detected")
except Exception as e:
    print(f"✗ Microphone error: {e}")

print("\n" + "="*50)
print("Setup complete! Run: python eva.py")
print("="*50)