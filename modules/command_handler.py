import os
import webbrowser
from modules.open_camera import open_camera
from modules.get_time_date import get_time, get_date
from modules.open_website import open_website

def handle_command(command):
    """
    Process user commands and execute appropriate actions
    
    Args:
        command (str): User voice command
        
    Returns:
        str: Response message or None
    """
    command = command.lower()
    
    # Exit commands
    if 'exit' in command or 'quit' in command or 'bye' in command or 'stop' in command:
        return "exit"
    
    # Time command
    elif 'time' in command:
        current_time = get_time()
        return f"The current time is {current_time}"
    
    # Date command
    elif 'date' in command:
        current_date = get_date()
        return f"Today's date is {current_date}"
    
    # Camera command
    elif 'camera' in command or 'webcam' in command:
        return open_camera()
    
    # Open applications
    elif 'open notepad' in command:
        os.system('notepad')
        return "Opening Notepad"
    
    elif 'open calculator' in command or 'open calc' in command:
        os.system('calc')
        return "Opening Calculator"
    
    elif 'open paint' in command:
        os.system('mspaint')
        return "Opening Paint"
    
    elif 'open command prompt' in command or 'open cmd' in command:
        os.system('start cmd')
        return "Opening Command Prompt"
    
    elif 'open file explorer' in command or 'open explorer' in command:
        os.system('explorer')
        return "Opening File Explorer"
    
    # Open websites
    elif 'open google' in command:
        return open_website('google.com', 'Google')
    
    elif 'open youtube' in command:
        return open_website('youtube.com', 'YouTube')
    
    elif 'open github' in command:
        return open_website('github.com', 'GitHub')
    
    elif 'open stack overflow' in command:
        return open_website('stackoverflow.com', 'Stack Overflow')
    
    # System commands
    elif 'shutdown' in command:
        os.system('shutdown /s /t 1')
        return "Shutting down the system"
    
    elif 'restart' in command:
        os.system('shutdown /r /t 1')
        return "Restarting the system"
    
    # Unknown command
    else:
        return "Sorry, I didn't understand that command. Please try again."