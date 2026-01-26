import logging
import time

from .stt.stt import RECOGNIZER, MIC, TRIGGER_WORD, CONVERSATION_TIMEOUT
from .tts.tts import speak_text
from .ai.agent import Agent
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)

logging.info("Setting up Agent")
agent = Agent()
logging.info("Agent Set up")


def main():
    conversation_mode = False
    last_interaction_time = None

    try:
        with MIC as source:
            RECOGNIZER.adjust_for_ambient_noise(source)
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

                        for text in agent.stream_invoke(command):
                            if first:
                                first = False
                                logging.info("🤖 Sending command to agent...")

                            speak_text(text)


                        logging.info(f"✅ Agent finshed response")                        

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
                    logging.error(f"❌ Error during recognition or tool call: {e}")
                    time.sleep(1)

    except Exception as e:
        logging.critical(f"❌ Critical error in main loop: {e}")


if __name__ == "__main__":
    main()