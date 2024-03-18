from grab import grabber
from scribe import TextTranscriber
from engine import engine

def __main__():
    engine_instance = engine("prompts.json")
    engine_instance.return_result()
    

if __name__ == "__main__":
    __main__()