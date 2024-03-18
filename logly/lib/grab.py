from pynput.mouse import Button, Controller
from pynput import mouse
from PIL import ImageGrab
import keyboard
from scribe import TextTranscriber
from gpt import gpt
import subprocess
import pyperclip
import time


class grabber:

    def __init__(self, file_path="screenshot.jpg"):
        self.coords = [None, None]
        self.file_path = file_path
        self.scriber = TextTranscriber(file_path)
        self.gpt = gpt()
        
    def take_screenshot(self, file_path="screenshot.png"):
        command = f"screencapture -i {file_path}"
        subprocess.run(command, shell=True)
        print(f"Screenshot saved to {file_path}")

    def copy_and_get_text(self):
        keyboard.press_and_release('cmd+c')  # Copy command for macOS
        time.sleep(0.1)  # Allow some time for the copy action to complete
        text = pyperclip.paste()
        print(f"Copied text: {text}")
        return text
                
