from langchain.tools import tool
import time

def get_time():
    "Get the Current Time"
    return time.strftime("%H:%M:%S")

