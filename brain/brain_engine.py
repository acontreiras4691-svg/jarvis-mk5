# ==================================================
# 🧠 BRAIN ENGINE - JARVIS MK5
# ==================================================

from brain.intent_router import route_intent


class BrainEngine:

    def __init__(self, memoria, memoria_rag):

        self.memoria = memoria
        self.memoria_rag = memoria_rag

    # ------------------------------------------------
    # PROCESSAR TEXTO
    # ------------------------------------------------

    def processar(self, texto):

        try:

            intent = route_intent(texto)

            if intent["type"] == "command":

                acao = intent["action"]

                resposta = acao(texto)

                return resposta

            if intent["type"] == "chat":

                return None

        except Exception as e:

            print(f"Erro BrainEngine: {e}")

        return None