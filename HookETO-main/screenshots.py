import time
import pyautogui
from PIL import ImageGrab
from datetime import datetime

save_path = "screenshots/"

while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    screenshot = ImageGrab.grab()
    screenshot.save(f"{save_path}{current_time}.png")
    print(f"Screenshot taken at {current_time}")
    time.sleep(3)
