import os
from modules.open_camera import open_camera
from modules.get_time_date import get_time, get_date
from modules.open_website import open_website
try:
    from modules.open_website import universal_open
except:
    universal_open = None


def handle_command(command):
    """Main backend command handler. Must return a string response."""
    
    if not command:
        return "No command detected."

    command = command.lower()

    # ---------------------------
    # GREETINGS
    # ---------------------------
    if "hello" in command or "hi" in command:
        return "Hello! How can I assist you?"

    # ---------------------------
    # TIME & DATE
    # ---------------------------
    if "time" in command:
        return f"The current time is {get_time()}"

    if "date" in command:
        return f"Today's date is {get_date()}"

    # ---------------------------
    # UNIVERSAL OPEN (if available)
    # ---------------------------
    if "open" in command and universal_open is not None:
        return universal_open(command)

    # ---------------------------
    # CAMERA OPERATIONS
    # ---------------------------
    if "capture photo" in command or "take photo" in command:
        from modules.open_camera import capture_photo
        result = capture_photo()
        return f"Photo captured successfully: {result}"

    if "record video" in command:
        from modules.open_camera import record_video
        result = record_video(5)
        return f"Video recorded successfully: {result}"

    if "switch camera" in command:
        from modules.open_camera import switch_camera
        camera_id = switch_camera(0)
        result = open_camera(camera_id)
        return f"Camera switched: {result}"

    # ---------------------------
    # OPEN WINDOWS APPLICATIONS
    # ---------------------------
    if "open notepad" in command:
        os.system("notepad")
        return "Opening Notepad"

    if "open calculator" in command or "open calc" in command:
        os.system("calc")
        return "Opening Calculator"

    if "open paint" in command:
        os.system("mspaint")
        return "Opening Paint"

    if "open command prompt" in command or "open cmd" in command:
        os.system("start cmd")
        return "Opening Command Prompt"

    if "open file explorer" in command or "open explorer" in command:
        os.system("explorer")
        return "Opening File Explorer"

    # ---------------------------
    # OPEN WEBSITES
    # ---------------------------
    if "open google" in command:
        return open_website("google.com", "Google")

    if "open youtube" in command:
        return open_website("youtube.com", "YouTube")

    if "open github" in command:
        return open_website("github.com", "GitHub")

    if "open stack overflow" in command:
        return open_website("stackoverflow.com", "Stack Overflow")

    # ---------------------------
    # SYSTEM CONTROLS
    # ---------------------------
    if "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down the system."

    if "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting the system."

    # ---------------------------
    # EXIT / QUIT
    # ---------------------------
    if "exit" in command or "quit" in command or "bye" in command:
        return "exit"

    # ---------------------------
    # UNKNOWN COMMAND
    # ---------------------------
    return f"I'm not sure how to handle '{command}'."
