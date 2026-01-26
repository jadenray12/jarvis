import pyttsx3
import logging
import time


def speak_text(text: str):
    try:
        engine = pyttsx3.init()

        voices = engine.getProperty('voices')        
        
        engine.setProperty("voice", voices[1].id)

        engine.setProperty("rate", 180)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.3)
    except Exception as e:
        logging.error(f"❌ TTS failed: {e}")
