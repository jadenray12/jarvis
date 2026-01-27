import logging
import time
import threading
import audioop

from .stt.stt import RECOGNIZER, MIC, TRIGGER_WORD, CONVERSATION_TIMEOUT
from .tts.tts import speak_text, stop_speaking, is_speaking
from .ai.agent import Agent
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)

logging.info("Setting up Agent")
agent = Agent()
logging.info("Agent Set up")


class InterruptHandler:
    def __init__(self):
        self.should_stop = False
        self.is_responding = False
        self.lock = threading.Lock()
        
    def start_response(self):
        with self.lock:
            self.should_stop = False
            self.is_responding = True
            
    def stop_response(self):
        with self.lock:
            self.is_responding = False
            
    def request_stop(self):
        with self.lock:
            self.should_stop = True
            stop_speaking()
            
    def should_interrupt(self):
        with self.lock:
            return self.should_stop


interrupt_handler = InterruptHandler()


def background_interrupt_listener(source):
    """Runs in background, detects loud audio (user speaking over TTS)"""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000  # Higher threshold for loud interrupts
    recognizer.dynamic_energy_threshold = False
    
    while True:
        try:
            if not interrupt_handler.is_responding:
                time.sleep(0.1)
                continue
                
            # Quick check for loud audio
            audio = recognizer.listen(source, timeout=0.3, phrase_time_limit=1)
            
            # Calculate volume
            rms = audioop.rms(audio.frame_data, audio.sample_width)
            
            # If it's loud enough (user speaking), interrupt
            if rms > 2000:  # Adjust this threshold
                logging.info(f"🛑 Loud audio detected (RMS: {rms}), interrupting!")
                interrupt_handler.request_stop()
                
        except sr.WaitTimeoutError:
            continue
        except Exception as e:
            continue


def main():
    conversation_mode = False
    last_interaction_time = None

    try:
        with MIC as source:
            RECOGNIZER.adjust_for_ambient_noise(source)
            
            # Start background interrupt listener
            listener_thread = threading.Thread(target=background_interrupt_listener, args=(source,), daemon=True)
            listener_thread.start()
            
            while True:
                try:
                    if not conversation_mode:
                        print("🎤 Listening for wake word...")
                        audio = RECOGNIZER.listen(source, timeout=10)
                        transcript = RECOGNIZER.recognize_google(audio)
                        print(f"🗣 Heard: {transcript}")

                        if TRIGGER_WORD.lower() in transcript.lower():
                            print(f"🗣 Triggered by: {transcript}")
                            speak_text("Yes sir?")
                            conversation_mode = True
                            last_interaction_time = time.time()
                        else:
                            print("Wake word not detected, continuing...")
                    else:
                        print("🎤 Listening for next command...")
                        audio = RECOGNIZER.listen(source, timeout=10)
                        command = RECOGNIZER.recognize_google(audio)

                        logging.info(f"✅ Agent heard: {command}")

                        first = True
                        interrupt_handler.start_response()

                        for text in agent.stream_invoke(command):
                            if interrupt_handler.should_interrupt():
                                logging.info("🛑 Response interrupted by user")
                                break
                                
                            if first:
                                first = False
                                logging.info("🤖 Sending command to agent...")

                            speak_text(text)
                            
                            if interrupt_handler.should_interrupt():
                                logging.info("🛑 Response interrupted by user")
                                break

                        interrupt_handler.stop_response()
                        logging.info(f"✅ Agent finished response")                        

                        last_interaction_time = time.time()

                        if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                            logging.info("⌛ Timeout: Returning to wake word mode.")
                            conversation_mode = False

                except sr.WaitTimeoutError:
                    logging.warning("⚠️ Timeout waiting for audio.")
                    if (
                        conversation_mode
                    ):
                        logging.info(
                            "⌛ No input in conversation mode. Returning to wake word mode."
                        )
                        conversation_mode = False
                except sr.UnknownValueError:
                    logging.warning("⚠️ Could not understand audio.")
                except Exception as e:
                    logging.error(f"⚠ Error during recognition or tool call: {e}")
                    time.sleep(1)

    except Exception as e:
        logging.critical(f"⚠ Critical error in main loop: {e}")


if __name__ == "__main__":
    main()