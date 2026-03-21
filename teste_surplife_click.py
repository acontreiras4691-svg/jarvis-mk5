import time
import pyautogui
import pygetwindow as gw

NOME_JANELA = "LDPlayer"

# Coordenadas RELATIVAS à janela do LDPlayer
# Ajusta depois se preciso
BTN_LUZ_QUARTO_X = 700
BTN_LUZ_QUARTO_Y = 255

def focar_ldplayer():
    wins = [w for w in gw.getWindowsWithTitle(NOME_JANELA) if w.title.strip()]
    if not wins:
        raise RuntimeError("Não encontrei a janela do LDPlayer.")
    win = wins[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)
    return win

def clicar_relativo(win, x, y):
    abs_x = win.left + x
    abs_y = win.top + y
    pyautogui.click(abs_x, abs_y)

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    time.sleep(2)
    win = focar_ldplayer()
    clicar_relativo(win, BTN_LUZ_QUARTO_X, BTN_LUZ_QUARTO_Y)