import time
import pyautogui
import pygetwindow as gw

NOME_JANELA = "LDPlayer"

wins = [w for w in gw.getWindowsWithTitle(NOME_JANELA) if w.title.strip()]
if not wins:
    raise RuntimeError("Não encontrei a janela do LDPlayer.")

win = wins[0]

if win.isMinimized:
    win.restore()
    time.sleep(1)

try:
    win.activate()
except Exception:
    pass

time.sleep(1)

print(f"Janela: left={win.left}, top={win.top}, width={win.width}, height={win.height}")
print("Mete o rato MESMO em cima do toggle da Luz Quarto dentro da janela. Ctrl+C para parar.\n")

try:
    while True:
        x, y = pyautogui.position()
        rel_x = x - win.left
        rel_y = y - win.top
        dentro = 0 <= rel_x <= win.width and 0 <= rel_y <= win.height
        print(f"\rABS=({x},{y})  REL=({rel_x},{rel_y})  DENTRO={dentro}", end="")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nParado.")