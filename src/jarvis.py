from RealtimeSTT import AudioToTextRecorder
def process_text(text):
    """Called when speech is detected and transcribed"""
    print(f"✅ You said: {text}\n")
    print("🎙️ Ready for next input...\n")
    # TODO: Send to Claude API for response



if __name__ == '__main__':
    print("=" * 60)
    print("🤖 JARVIS ONLINE")
    print("=" * 60)
    print("Speak naturally - I'll transcribe when you're done talking\n")
    
    recorder = AudioToTextRecorder(
        model="base",
        language="en",
        wake_words="jarvis",
        wakeword_backend="openwakeword",
        wake_words_sensitivity=0.6,        
        # Callback when wake word is detected
        on_wakeword_detected=play_sound  # Beep happens here!
    )
    
    print("🎙️ Listening...\n")
    
    try:
        while True:

                print(recorder.text())
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("👋 JARVIS shutting down...")
        print("=" * 60)