import json
import keyboard
from grab import grabber
from gpt import gpt
from scribe import TextTranscriber

class engine:
    def __init__(self, prompt_file):
        self.file = prompt_file
        self.keys = self.get_keys_from_json_file()
        self.grabber = grabber()
        self.scriber = TextTranscriber("screenshot.jpg")
        self.gpt = gpt()
        
    def get_content_with_snippet(self, key, snippet):
        with open(self.file, 'r') as f:
            prompts = json.load(f)

        messages = prompts[key]
        for message in messages:
            if '{snippet}' in message['content']:
                message['content'] = message['content'].replace('{snippet}', snippet)
                break

        return messages  # Return the array of messages

    
    def get_keys_from_json_file(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
            
        return list(data.keys())
    
    def handle_key_combination(self, valid_key):
        copied_text = self.grabber.copy_and_get_text()
        message = self.get_content_with_snippet(valid_key, copied_text)
        resolution = self.gpt.q_and_a(message, 1000, 0.9)
        print(f"Resolution: {resolution}")
        print("Press CMD + your short cut key to copy more highlighted text...")

    def handle_cmd_ctrl(self):
        print("CMD + CTRL + key combination detected...")
        for valid_key in self.keys:
            if keyboard.is_pressed(valid_key):
                self.grabber.take_screenshot()
                extracted_text = self.scriber.transcribe()
                message = self.get_content_with_snippet(valid_key, extracted_text)
                resolution = self.gpt.q_and_a(message, 1000, 0.9)
                print(f"Resolution: {resolution}")
                break

    def return_result(self):
        print("Press CMD + your short cut key to get started...")

        for valid_key in self.keys:
            hotkey = 'cmd+' + valid_key
            keyboard.add_hotkey(hotkey, lambda e=valid_key: self.handle_key_combination(e))

            shift_hotkey = 'cmd+ctrl+' + valid_key
            keyboard.add_hotkey(shift_hotkey, lambda e=valid_key: self.handle_cmd_ctrl(e))

        print("Hotkeys are set up. Waiting for key combinations...")
        keyboard.wait()  # This will keep the program running indefinitely
