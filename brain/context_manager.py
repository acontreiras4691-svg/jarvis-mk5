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
        if valor is not None:
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
        """
        Atualiza contexto sem deixar valores None apagarem contexto válido.
        """
        if self.expirado():
            self.clear()

        houve_update = False

        for chave, valor in dados.items():
            if valor is not None:
                self.contexto[chave] = valor
                houve_update = True

        if houve_update:
            self.ultimo_update = time.time()

    # ------------------------------------------------

    def enrich(self, dados: dict) -> dict:
        """
        Preenche campos em falta com contexto anterior ainda válido.
        """
        if self.expirado():
            self.clear()
            return dados

        resultado = dict(dados)

        for chave, valor in self.contexto.items():
            if resultado.get(chave) is None:
                resultado[chave] = valor

        return resultado

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