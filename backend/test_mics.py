import speech_recognition as sr

MIC_INDEX = 5  # from your test_mics.py

r = sr.Recognizer()

print(f"[TEST] Using device index: {MIC_INDEX}")
print("[TEST] Listing microphones:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  {i}: {name}")

with sr.Microphone(device_index=MIC_INDEX) as source:
    print("\n[TEST] Adjusting for ambient noise (0.5s)...")
    r.dynamic_energy_threshold = False
    r.energy_threshold = 120   # try 80–150 if needed
    r.pause_threshold = 0.8
    r.adjust_for_ambient_noise(source, duration=0.5)

    print("[TEST] Listening... Speak clearly (e.g., 'open google')...")
    audio = r.listen(source, timeout=10, phrase_time_limit=6)

print("[TEST] Got audio, sending to Google STT...")

try:
    text = r.recognize_google(audio, language="en-US")
    print(f"[TEST] Recognized: {text!r}")
except sr.WaitTimeoutError:
    print("[TEST] Timeout – no speech detected")
except sr.UnknownValueError:
    print("[TEST] Could not understand audio")
except sr.RequestError as e:
    print(f"[TEST] STT request error: {e}")
