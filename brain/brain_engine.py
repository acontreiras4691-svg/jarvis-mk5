# ==================================================
# 🧠 BRAIN ENGINE - JARVIS MK5
# ==================================================

from brain.intent_router import IntentRouter
from executor.executor_engine import Executor


class BrainEngine:

    def __init__(self, memoria, memoria_rag, smart_home=None):
        self.memoria = memoria
        self.memoria_rag = memoria_rag

        self.router = IntentRouter()
        self.executor = Executor(smart_home=smart_home)

        # contexto curto de conversa
        self.ultimo_texto = ""
        self.ultimo_intent = None
        self.ultimas_entities = {}

    # ------------------------------------------------
    # GUARDAR CONTEXTO
    # ------------------------------------------------

    def guardar_contexto(self, texto: str, intent_data: dict):
        self.ultimo_texto = texto
        self.ultimo_intent = intent_data.get("intent")
        self.ultimas_entities = intent_data.get("entities", {}) or {}

    # ------------------------------------------------
    # FOLLOW-UP
    # ------------------------------------------------

    def eh_followup(self, texto: str) -> bool:
        texto = texto.lower().strip()

        followups = [
            "e ",
            "entao ",
            "então ",
            "e em ",
            "e no ",
            "e na ",
            "e amanhã",
            "e amanha",
            "e depois",
            "e agora",
        ]

        return any(texto.startswith(f) for f in followups)

    def resolver_followup(self, texto: str) -> str:
        texto_lower = texto.lower().strip()

        if not self.ultimo_intent:
            return texto

        # ---------------------------------------------
        # FOLLOW-UP DE HORAS
        # ---------------------------------------------
        if self.ultimo_intent == "assistant.time":

            if "portugal" in texto_lower:
                return "que horas são em Portugal"

            if "amanhã" in texto_lower or "amanha" in texto_lower:
                return "que horas serão amanhã"

            if texto_lower.startswith("e "):
                return f"que horas são {texto_lower[2:].strip()}"

        # ---------------------------------------------
        # FOLLOW-UP DE DATA
        # ---------------------------------------------
        if self.ultimo_intent == "assistant.date":

            if "amanhã" in texto_lower or "amanha" in texto_lower:
                return "que dia será amanhã"

            if texto_lower.startswith("e "):
                return f"que dia é {texto_lower[2:].strip()}"

        # ---------------------------------------------
        # FOLLOW-UP SMART HOME
        # ---------------------------------------------
        if self.ultimo_intent in [
            "smart_home.light_on",
            "smart_home.light_off",
            "smart_home.plug_on",
            "smart_home.plug_off",
        ]:
            if texto_lower.startswith("e no ") or texto_lower.startswith("e na "):
                acao = self.ultimas_entities.get("action")
                device_type = self.ultimas_entities.get("device_type", "light")

                local = texto_lower.replace("e no ", "").replace("e na ", "").strip()

                if acao == "turn_on" and device_type == "light":
                    return f"acende a luz no {local}"

                if acao == "turn_off" and device_type == "light":
                    return f"apaga a luz no {local}"

                if acao == "turn_on" and device_type == "plug":
                    return f"liga a tomada no {local}"

                if acao == "turn_off" and device_type == "plug":
                    return f"desliga a tomada no {local}"

        # ---------------------------------------------
        # FOLLOW-UP DE ABRIR APP
        # ---------------------------------------------
        if self.ultimo_intent == "system.open_app":
            if texto_lower.startswith("e o ") or texto_lower.startswith("e a "):
                resto = texto_lower[4:].strip()
                return f"abre {resto}"

            if texto_lower.startswith("e "):
                return f"abre {texto_lower[2:].strip()}"

        return texto

    # ------------------------------------------------
    # RESPOSTAS INSTANTÂNEAS
    # ------------------------------------------------

    def resposta_instantanea(self, texto: str):
        texto = texto.lower().strip()

        if texto in ["olá", "ola", "olá jarvis", "ola jarvis"]:
            return "Bom dia, Dudu."

        if "obrigado" in texto or "obrigada" in texto:
            return "Sempre às ordens."

        if "bom trabalho" in texto:
            return "Naturalmente."

        return None

    # ------------------------------------------------
    # PROCESSAR
    # ------------------------------------------------

    def processar(self, texto: str):

        try:
            texto = texto.strip()

            # 1. follow-up contextual
            if self.eh_followup(texto):
                texto = self.resolver_followup(texto)

            # 2. resposta instantânea
            resposta = self.resposta_instantanea(texto)
            if resposta:
                return resposta

            # 3. router
            resultado = self.router.route_intent(texto)

            tipo = resultado.get("type")

            # 4. comando local
            if tipo == "command":
                self.guardar_contexto(texto, resultado)

                resposta = self.executor.executar(resultado)

                if resposta:
                    return resposta

                return "Não consegui executar o comando."

            # 5. chat / servidor
            if tipo == "chat":
                self.guardar_contexto(texto, resultado)
                return None

            return None

        except Exception as e:
            print(f"Erro BrainEngine: {e}")
            return "Erro interno no cérebro do Jarvis."