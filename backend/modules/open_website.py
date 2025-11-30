import webbrowser

def open_website(url, name):
    """
    Open a website in default browser
    
    Args:
        url (str): Website URL
        name (str): Website name for response
        
    Returns:
        str: Confirmation message
    """
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        
        webbrowser.open(url)
        return f"Opening {name}"
        
    except Exception as e:
        return f"Error opening website: {str(e)}"