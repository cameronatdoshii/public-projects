import easyocr
from process import processor
import time

class TextTranscriber:

    def __init__(self, image_path):
        self.image_path = image_path
        self.processor = processor()

    def transcribe(self):
        start_time = time.time() # Record the start time

        reader = easyocr.Reader(lang_list=['en']) # Specify the language(s) you need
        results = reader.readtext(self.image_path, detail=0)
        full_text = ' '.join(results) # Concatenate all text regions into one string

        end_time = time.time() # Record the end time

        #print(f"Transcribed text: {full_text}")
        #print(f"Time taken: {end_time - start_time} seconds")
        return full_text