from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage, ToolMessage

from ..tts.tts import speak_text
from .tools.time import get_time
class Agent:
    def __init__(self):
        self.llm = ChatOllama(model="qwen3:1.7b")
        self.agent = create_agent(self.llm,
                                  tools = [get_time],
                                  system_prompt = SystemMessage(content="You are a helpful assistant JARVIS from Ironman. Be nice and friendly and answer user queries. Do not use emojis in your responses")

                                  )
        

    def invoke(self, text: str):
        # Wrap the text in a dict with the correct key
        # The key should match your graph's state schema
        result = self.agent.invoke({"messages": [{"role": "user", "content": text}]})
        return result
    

    def stream_invoke(self, text:str):
    
        inputs = {"messages": [HumanMessage(content=text)]}
        sentence_buffer = ""

        for chunk in self.agent.stream(inputs, stream_mode="messages"):
            if isinstance(chunk[0], ToolMessage):
                continue


            token = chunk[0].content
            if not token:
                continue

            print(token, end="", flush=True) # Still print for the UI
            sentence_buffer += token

            # Check if we have a complete sentence
            if any(punc in token for punc in [".", "!", "?", "\n"]):
                # Clean up the string and send to TTS
                speech_text = sentence_buffer.strip()
                if speech_text:
                    # Replace 'your_tts_function' with your actual TTS call
                    yield speech_text
                
                sentence_buffer = "" # Reset for the next sentence

        # Catch any remaining text (e.g., if it didn't end with punctuation)
        if sentence_buffer.strip():
            yield sentence_buffer.strip()

