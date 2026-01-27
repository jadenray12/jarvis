import pyttsx3
import logging
import threading


class InterruptibleTTS:
    def __init__(self):
        self.engine = None
        self.speaking = False
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        
    def speak_text(self, text: str):
        try:
            with self.lock:
                self.stop_flag.clear()
                self.speaking = True
                
                if self.engine is None:
                    self.engine = pyttsx3.init()
                    voices = self.engine.getProperty('voices')
                    self.engine.setProperty("voice", voices[1].id)
                    self.engine.setProperty("rate", 180)
                    self.engine.setProperty("volume", 1.0)
                
                self.engine.say(text)
                self.engine.startLoop(False)
                
                while self.engine.isBusy() and not self.stop_flag.is_set():
                    self.engine.iterate()
                
                self.engine.endLoop()
                self.speaking = False
                
        except Exception as e:
            logging.error(f"⚠ TTS failed: {e}")
            self.speaking = False
    
    def stop(self):
        self.stop_flag.set()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


tts_instance = InterruptibleTTS()


def speak_text(text: str):
    tts_instance.speak_text(text)


def stop_speaking():
    tts_instance.stop()


def is_speaking():
    return tts_instance.speaking