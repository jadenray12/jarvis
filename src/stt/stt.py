import os
import logging
import time
import speech_recognition as sr


MIC_INDEX = None
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30  

RECOGNIZER = sr.Recognizer()
MIC = sr.Microphone(device_index=MIC_INDEX)




        



# Main interaction loop
