import eel

@eel.expose
def send_to_python(message):
    print(f"Message received from JavaScript: {message}")
