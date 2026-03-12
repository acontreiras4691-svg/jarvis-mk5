# ==================================================
# 🧠 BRAIN ENGINE - JARVIS MK5 (FIXED)
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

            resultado = route_intent(texto)

            intent = resultado.get("intent")
            entities = resultado.get("entities", {})

            # -------------------------
            # COMANDO
            # -------------------------

            if intent == "COMANDO":

                resposta = executar({
                    "intent": intent,
                    "entities": entities
                })

                return resposta

            # -------------------------
            # FACTUAL
            # -------------------------

            if intent == "FACTUAL":

                return None

            # -------------------------
            # CHAT / RACIOCINIO
            # -------------------------

            return None

        except Exception as e:

            print(f"Erro BrainEngine: {e}")

        return None