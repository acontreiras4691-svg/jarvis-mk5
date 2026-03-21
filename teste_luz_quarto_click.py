import time
import pyautogui

# Coordenadas ABSOLUTAS do botão da luz
X_BOTAO = -1470
Y_BOTAO = 379

pyautogui.FAILSAFE = True

print("Vou clicar no botão da Luz Quarto em 3 segundos...")
time.sleep(3)

pyautogui.click(X_BOTAO, Y_BOTAO)

print("Clique enviado.")