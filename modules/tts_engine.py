import pyttsx3

_engine = pyttsx3.init()
_engine.setProperty('rate', 135)  # You can adjust speed here if needed
_engine.setProperty('volume', 0.9)
# Set the voice to Microsoft Prabhat (English - India)
for voice in _engine.getProperty('voices'):
    if "Mark" in voice.name:
        _engine.setProperty('voice', voice.id)
        break

def speak(text):
    _engine.say(text)
    _engine.runAndWait()
