# ==================================================
# 🧠 CONTEXT MANAGER - JARVIS MK5
# ==================================================

import time


class ContextManager:

    def __init__(self):
        self.contexto = {}
        self.expiracao = 60  # segundos
        self.ultimo_update = 0

    # ------------------------------------------------

    def set(self, chave, valor):
        self.contexto[chave] = valor
        self.ultimo_update = time.time()

    # ------------------------------------------------

    def get(self, chave, default=None):
        if self.expirado():
            self.clear()
            return default

        return self.contexto.get(chave, default)

    # ------------------------------------------------

    def update(self, dados: dict):
        self.contexto.update(dados)
        self.ultimo_update = time.time()

    # ------------------------------------------------

    def clear(self):
        self.contexto = {}
        self.ultimo_update = 0

    # ------------------------------------------------

    def expirado(self):
        if self.ultimo_update == 0:
            return False

        return (time.time() - self.ultimo_update) > self.expiracao

    # ------------------------------------------------

    def dump(self):
        if self.expirado():
            self.clear()

        return dict(self.contexto)