import time
import pyautogui

print("Mexe o rato para cima do botão da luz. Ctrl+C para parar.\n")
try:
    while True:
        x, y = pyautogui.position()
        print(f"\rX={x} Y={y}", end="")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nParado.")