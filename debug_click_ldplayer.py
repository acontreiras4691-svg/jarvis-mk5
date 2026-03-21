import time
import pyautogui
import pygetwindow as gw

# Coordenadas ABSOLUTAS que apanhaste com o rato
X_BOTAO = -1470
Y_BOTAO = 379

NOME_JANELA = "LDPlayer"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def focar_ldplayer():
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
    return win


print("Vou focar o LDPlayer e mover o rato em 3 segundos...")
time.sleep(3)

win = focar_ldplayer()

print(f"Janela LDPlayer: left={win.left}, top={win.top}, width={win.width}, height={win.height}")
print(f"Vou mover para X={X_BOTAO}, Y={Y_BOTAO}")

# mover visivelmente
pyautogui.moveTo(X_BOTAO, Y_BOTAO, duration=1.0)

# pequeno pause para veres onde foi parar
time.sleep(1)

# 3 cliques para não haver dúvidas
pyautogui.click()
time.sleep(0.5)
pyautogui.click()
time.sleep(0.5)
pyautogui.click()

print("Fim.")