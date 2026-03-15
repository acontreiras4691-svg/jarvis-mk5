# ==================================================
# 🧠 BRAIN ENGINE - JARVIS MK5
# ==================================================

from brain.intent_router import IntentRouter
from brain.context_manager import ContextManager
from executor.executor_engine import Executor


class BrainEngine:

    def __init__(self, memoria, memoria_rag, smart_home=None):
        self.memoria = memoria
        self.memoria_rag = memoria_rag

        self.router = IntentRouter()
        self.executor = Executor(smart_home=smart_home)

        self.ultimo_texto = ""
        self.ultimo_intent = None
        self.ultimas_entities = {}

        self.context = ContextManager()

    # ------------------------------------------------
    # CONTEXTO CURTO
    # ------------------------------------------------

    def guardar_contexto(self, texto: str, intent_data: dict):
        self.ultimo_texto = texto
        self.ultimo_intent = intent_data.get("intent")
        self.ultimas_entities = intent_data.get("entities", {}) or {}

        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        dados_contexto = {
            "last_text": texto,
            "last_intent": intent,
        }

        if entities.get("location"):
            dados_contexto["last_location"] = entities.get("location")

        if entities.get("device_type"):
            dados_contexto["last_device_type"] = entities.get("device_type")

        if entities.get("action"):
            dados_contexto["last_action"] = entities.get("action")

        if entities.get("app"):
            dados_contexto["last_app"] = entities.get("app")

        if entities.get("brightness") is not None:
            dados_contexto["last_brightness"] = entities.get("brightness")

        if entities.get("minutes") is not None:
            dados_contexto["last_minutes"] = entities.get("minutes")

        self.context.update(dados_contexto)

    # ------------------------------------------------
    # FOLLOW-UP
    # ------------------------------------------------

    def eh_followup(self, texto: str) -> bool:
        texto = texto.lower().strip()

        starts = [
            "e ",
            "entao ",
            "então ",
            "agora ",
            "depois ",
            "e em ",
            "e no ",
            "e na ",
            "e amanhã",
            "e amanha",
            "e depois",
            "e também",
            "tambem ",
            "também ",
            "baixa ",
            "aumenta ",
            "mete ",
            "poe ",
            "põe ",
            "apaga em ",
            "apaga daqui a ",
            "desliga em ",
            "desliga daqui a ",
        ]

        return any(texto.startswith(x) for x in starts)

    def resolver_followup(self, texto: str) -> str:
        texto_lower = texto.lower().strip()

        if not self.ultimo_intent:
            return texto

        # ---------------------------------------------
        # FOLLOW-UP DE HORAS
        # ---------------------------------------------
        if self.ultimo_intent == "assistant.time":

            if "portugal" in texto_lower:
                return "que horas são em portugal"

            if "suica" in texto_lower or "suíça" in texto_lower:
                return "que horas são na suica"

            if "espanha" in texto_lower:
                return "que horas são em espanha"

            if "franca" in texto_lower or "frança" in texto_lower:
                return "que horas são na franca"

            if "lausanne" in texto_lower:
                return "que horas são em lausanne"

            if "lisboa" in texto_lower:
                return "que horas são em lisboa"

            if "amanhã" in texto_lower or "amanha" in texto_lower:
                return "que horas serão amanhã"

            if texto_lower.startswith("e "):
                resto = texto_lower[2:].strip()
                return f"que horas são {resto}"

        # ---------------------------------------------
        # FOLLOW-UP DE DATA
        # ---------------------------------------------
        if self.ultimo_intent == "assistant.date":

            if "amanhã" in texto_lower or "amanha" in texto_lower:
                return "que dia será amanhã"

            if "portugal" in texto_lower:
                return "que dia é hoje em portugal"

            if "espanha" in texto_lower:
                return "que dia é hoje em espanha"

            if "franca" in texto_lower or "frança" in texto_lower:
                return "que dia é hoje na franca"

            if texto_lower.startswith("e "):
                resto = texto_lower[2:].strip()
                return f"que dia é {resto}"

        # ---------------------------------------------
        # FOLLOW-UP SMART HOME ON/OFF
        # ---------------------------------------------
        if self.ultimo_intent in [
            "smart_home.light_on",
            "smart_home.light_off",
            "smart_home.plug_on",
            "smart_home.plug_off",
            "smart_home.light_set_brightness",
            "smart_home.light_off_timer",
        ]:
            acao = self.context.get("last_action", self.ultimas_entities.get("action"))
            device_type = self.context.get(
                "last_device_type",
                self.ultimas_entities.get("device_type", "light")
            )
            last_location = self.context.get("last_location")

            # divisão omitida
            if texto_lower.startswith("e no "):
                local = texto_lower.replace("e no ", "", 1).strip()

                if device_type == "light" and acao == "turn_on":
                    return f"acende a luz no {local}"
                if device_type == "light" and acao == "turn_off":
                    return f"apaga a luz no {local}"
                if device_type == "plug" and acao == "turn_on":
                    return f"liga a tomada no {local}"
                if device_type == "plug" and acao == "turn_off":
                    return f"desliga a tomada no {local}"

            if texto_lower.startswith("e na "):
                local = texto_lower.replace("e na ", "", 1).strip()

                if device_type == "light" and acao == "turn_on":
                    return f"acende a luz na {local}"
                if device_type == "light" and acao == "turn_off":
                    return f"apaga a luz na {local}"
                if device_type == "plug" and acao == "turn_on":
                    return f"liga a tomada na {local}"
                if device_type == "plug" and acao == "turn_off":
                    return f"desliga a tomada na {local}"

            # brilho omitindo divisão
            if (
                "metade" in texto_lower
                or "brilho" in texto_lower
                or "intensidade" in texto_lower
                or texto_lower.startswith("baixa")
                or texto_lower.startswith("aumenta")
                or texto_lower.startswith("mete")
                or texto_lower.startswith("poe")
                or texto_lower.startswith("põe")
            ):
                if last_location:
                    return f"mete a luz no {last_location} para metade"
                return "mete a luz para metade"

            # temporizador omitindo divisão
            if (
                texto_lower.startswith("apaga em ")
                or texto_lower.startswith("apaga daqui a ")
                or texto_lower.startswith("desliga em ")
                or texto_lower.startswith("desliga daqui a ")
            ):
                if last_location:
                    return f"apaga a luz no {last_location} {texto_lower}"
                return f"apaga a luz {texto_lower}"

        # ---------------------------------------------
        # FOLLOW-UP DE APPS
        # ---------------------------------------------
        if self.ultimo_intent == "system.open_app":
            if texto_lower.startswith("e "):
                resto = texto_lower[2:].strip()
                return f"abre {resto}"

        return texto

    # ------------------------------------------------
    # RESPOSTAS INSTANTÂNEAS
    # ------------------------------------------------

    def resposta_instantanea(self, texto: str):
        texto = texto.lower().strip()

        if texto in ["olá", "ola", "olá jarvis", "ola jarvis"]:
            return {
                "text": "Olá, Dudu.",
                "end_conversation": False,
            }

        if "obrigado" in texto or "obrigada" in texto:
            return {
                "text": "Sempre às ordens.",
                "end_conversation": True,
            }

        if texto in ["tchau", "adeus", "até já", "ate ja", "até logo", "ate logo"]:
            return {
                "text": "Até já, Dudu.",
                "end_conversation": True,
            }

        if "bom trabalho" in texto:
            return {
                "text": "Naturalmente.",
                "end_conversation": False,
            }

        return None

    # ------------------------------------------------
    # PROCESSAR
    # ------------------------------------------------

    def processar(self, texto: str):
        try:
            texto = texto.strip()

            if self.eh_followup(texto):
                texto = self.resolver_followup(texto)

            resposta = self.resposta_instantanea(texto)
            if resposta:
                return resposta

            resultado = self.router.route_intent(texto)
            tipo = resultado.get("type")

            if tipo == "command":
                self.guardar_contexto(texto, resultado)

                resposta = self.executor.executar(resultado)

                if resposta:
                    return {
                        "text": resposta,
                        "end_conversation": False,
                    }

                return {
                    "text": "Não consegui executar o comando.",
                    "end_conversation": False,
                }

            if tipo == "chat":
                self.guardar_contexto(texto, resultado)
                return None

            return None

        except Exception as e:
            print(f"Erro BrainEngine: {e}")
            return {
                "text": "Erro interno no cérebro do Jarvis.",
                "end_conversation": True,
            }