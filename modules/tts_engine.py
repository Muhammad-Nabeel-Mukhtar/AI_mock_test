import pyttsx3

_engine = pyttsx3.init()
_engine.setProperty('rate', 150)

def speak(text):
    _engine.say(text)
    _engine.runAndWait()

