# ==================================================
# 🧠 BRAIN ENGINE - JARVIS MK5
# ==================================================

import re
import time

from brain.intent_router import IntentRouter
from executor.executor_engine import Executor
from core.logger import log


class BrainEngine:
    def __init__(self, memoria, memoria_rag, smart_home=None):
        self.memoria = memoria
        self.memoria_rag = memoria_rag
        self.smart_home = smart_home

        self.router = IntentRouter()
        self.executor = Executor(smart_home=smart_home)

        self.pending_confirmation = None

        self.confirm_yes = {
            "sim",
            "ya",
            "yah",
            "yap",
            "claro",
            "confirmo",
            "confirmar",
            "podes",
            "pode ser",
            "forca",
            "força",
            "avanca",
            "avança",
            "ok",
            "okay",
            "faz isso",
            "executa",
        }

        self.confirm_no = {
            "não",
            "nao",
            "nop",
            "nopes",
            "cancela",
            "cancelar",
            "para",
            "deixa",
            "afinal nao",
            "afinal não",
            "esquece",
            "esquecer",
            "nao quero",
            "não quero",
        }

        self.contexto_curto = {
            "location": None,
            "device_type": None,
            "last_intent": None,
            "updated_at": 0.0,
        }

        self.context_ttl = 45.0

    # ==================================================
    # HELPERS GERAIS
    # ==================================================

    def _normalizar(self, texto: str) -> str:
        return (texto or "").strip().lower()

    def _limpar_confirmacao(self):
        self.pending_confirmation = None

    def _guardar_confirmacao(self, intent_data: dict):
        self.pending_confirmation = intent_data

    def _precisa_confirmacao(self, intent_data: dict) -> bool:
        return bool(intent_data.get("requires_confirmation", False))

    def _texto_confirmacao(self, intent_data: dict) -> str:
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        if intent == "system.shutdown":
            return "Tens a certeza que queres desligar o computador?"

        if intent == "system.restart":
            return "Tens a certeza que queres reiniciar o computador?"

        if intent == "smart_home.light_off":
            location = entities.get("location")
            if location:
                return f"Tens a certeza que queres apagar a luz em {location}?"
            return "Tens a certeza que queres apagar a luz?"

        if intent == "smart_home.plug_off":
            location = entities.get("location")
            if location:
                return f"Tens a certeza que queres desligar a tomada em {location}?"
            return "Tens a certeza que queres desligar a tomada?"

        return "Tens a certeza que queres executar esse comando?"

    def _responder_confirmacao(self, texto: str):
        texto_norm = self._normalizar(texto)

        if not self.pending_confirmation:
            return None

        if texto_norm in self.confirm_yes:
            intent_data = self.pending_confirmation
            self._limpar_confirmacao()

            log("✅ Confirmação aceite.")

            try:
                resposta = self.executor.executar(intent_data)
            except Exception as e:
                log(f"❌ ERRO no Executor após confirmação: {e}")
                return {
                    "text": "Ocorreu um erro ao executar o comando confirmado.",
                    "end_conversation": True
                }

            if not resposta:
                resposta = "Comando confirmado, mas não consegui executar corretamente."

            self._atualizar_contexto(intent_data)

            return {
                "text": resposta,
                "end_conversation": False
            }

        if texto_norm in self.confirm_no:
            self._limpar_confirmacao()

            log("🛑 Confirmação cancelada pelo utilizador.")
            return {
                "text": "Comando cancelado.",
                "end_conversation": True
            }

        return {
            "text": "Responde só com sim ou não.",
            "end_conversation": False
        }

    # ==================================================
    # CONTEXTO CURTO
    # ==================================================

    def _contexto_valido(self) -> bool:
        updated_at = self.contexto_curto.get("updated_at", 0.0)
        if not updated_at:
            return False
        return (time.time() - updated_at) <= self.context_ttl

    def _limpar_contexto(self):
        self.contexto_curto = {
            "location": None,
            "device_type": None,
            "last_intent": None,
            "updated_at": 0.0,
        }

    def _atualizar_contexto(self, intent_data: dict):
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        intents_contexto = {
            "smart_home.light_on",
            "smart_home.light_off",
            "smart_home.light_set_brightness",
            "smart_home.light_off_timer",
            "smart_home.plug_on",
            "smart_home.plug_off",
        }

        if intent not in intents_contexto:
            return

        location = entities.get("location")
        device_type = entities.get("device_type")

        if not device_type:
            if "light" in intent:
                device_type = "light"
            elif "plug" in intent:
                device_type = "plug"

        if location or device_type:
            self.contexto_curto = {
                "location": location or self.contexto_curto.get("location"),
                "device_type": device_type or self.contexto_curto.get("device_type"),
                "last_intent": intent,
                "updated_at": time.time(),
            }

            log(
                f"🧠 Contexto atualizado -> "
                f"location={self.contexto_curto['location']} | "
                f"device_type={self.contexto_curto['device_type']} | "
                f"intent={self.contexto_curto['last_intent']}"
            )

    # ==================================================
    # FOLLOW-UP / ENRIQUECIMENTO
    # ==================================================

    def _extrair_location_followup(self, texto: str):
        texto_norm = self.router.normalizar(texto)

        # primeiro tenta a extração normal do router
        location = self.router.extract_smart_location(texto_norm)
        if location:
            return location

        # padrões simples de follow-up
        patterns = [
            r"\bno ([\wçãõáéíóú]+)\b",
            r"\bna ([\wçãõáéíóú]+)\b",
            r"\bdo ([\wçãõáéíóú]+)\b",
            r"\bda ([\wçãõáéíóú]+)\b",
        ]

        locais_validos = {
            "quarto",
            "sala",
            "cozinha",
            "escritorio",
            "escritório",
            "wc",
            "corredor",
        }

        for pattern in patterns:
            match = re.search(pattern, texto_norm)
            if match:
                possivel = match.group(1).strip()
                possivel = self.router.normalizar(possivel)

                if possivel in locais_validos:
                    if possivel == "escritorio":
                        return "escritório"
                    return possivel

        return None

    def _extrair_device_followup(self, texto: str):
        texto_norm = self.router.normalizar(texto)

        if "tomada" in texto_norm:
            return "plug"

        if "luz" in texto_norm:
            return "light"

        if "essa luz" in texto_norm or "a luz" in texto_norm:
            return "light"

        return None

    def _resolver_followup_incompleto(self, texto: str, intent_data: dict):
        """
        Só tenta inferir comando quando o router devolve chat.
        Exemplos:
        - 'na sala'
        - 'do wc'
        - 'a 20%'
        - 'desliga'
        - 'liga'
        - 'em 2 minutos'
        """
        if not self._contexto_valido():
            return intent_data

        if intent_data.get("type") != "chat":
            return intent_data

        texto_norm = self.router.normalizar(texto)
        location = self._extrair_location_followup(texto)
        device_type = self._extrair_device_followup(texto) or self.contexto_curto.get("device_type")
        last_location = self.contexto_curto.get("location")
        last_intent = self.contexto_curto.get("last_intent")

        # brilho curto: "a 20%" / "20%"
        brightness = self.router.extract_brightness(texto_norm)
        if brightness is not None:
            return {
                "type": "command",
                "intent": "smart_home.light_set_brightness",
                "entities": {
                    "location": location or last_location,
                    "device_type": "light",
                    "brightness": brightness,
                },
                "confidence": 0.78,
                "requires_confirmation": False,
            }

        # timer curto: "em 2 minutos"
        minutes = self.router.extract_minutes(texto_norm)
        if minutes is not None:
            # por agora timer é só para luz
            return {
                "type": "command",
                "intent": "smart_home.light_off_timer",
                "entities": {
                    "location": location or last_location,
                    "device_type": "light",
                    "minutes": minutes,
                },
                "confidence": 0.77,
                "requires_confirmation": False,
            }

        # follow-up curto: "liga"
        if texto_norm in {"liga", "acende"}:
            intent = "smart_home.light_on"
            if device_type == "plug":
                intent = "smart_home.plug_on"

            return {
                "type": "command",
                "intent": intent,
                "entities": {
                    "location": location or last_location,
                    "device_type": device_type or "light",
                    "action": "turn_on",
                },
                "confidence": 0.75,
                "requires_confirmation": False,
            }

        # follow-up curto: "desliga" / "apaga"
        if texto_norm in {"desliga", "apaga"}:
            intent = "smart_home.light_off"
            if device_type == "plug":
                intent = "smart_home.plug_off"

            return {
                "type": "command",
                "intent": intent,
                "entities": {
                    "location": location or last_location,
                    "device_type": device_type or "light",
                    "action": "turn_off",
                },
                "confidence": 0.75,
                "requires_confirmation": False,
            }

        # só mudança de local: "na sala" / "do wc"
        if location and last_intent:
            entities = {
                "location": location,
                "device_type": self.contexto_curto.get("device_type"),
            }

            if last_intent in {"smart_home.light_on", "smart_home.light_off"}:
                entities["action"] = "turn_on" if last_intent.endswith("light_on") else "turn_off"

            if last_intent in {"smart_home.plug_on", "smart_home.plug_off"}:
                entities["action"] = "turn_on" if last_intent.endswith("plug_on") else "turn_off"

            return {
                "type": "command",
                "intent": last_intent,
                "entities": entities,
                "confidence": 0.70,
                "requires_confirmation": False,
            }

        return intent_data

    def _enriquecer_com_contexto(self, intent_data: dict) -> dict:
        if not intent_data:
            return intent_data

        if not self._contexto_valido():
            return intent_data

        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        if not intent:
            return intent_data

        location_ctx = self.contexto_curto.get("location")
        device_ctx = self.contexto_curto.get("device_type")

        intents_smart = {
            "smart_home.light_on",
            "smart_home.light_off",
            "smart_home.light_set_brightness",
            "smart_home.light_off_timer",
            "smart_home.plug_on",
            "smart_home.plug_off",
        }

        if intent not in intents_smart:
            return intent_data

        if not entities.get("location") and location_ctx:
            entities["location"] = location_ctx

        if not entities.get("device_type") and device_ctx:
            entities["device_type"] = device_ctx

        # reforçar pelo intent real
        if "light" in intent:
            entities["device_type"] = "light"

        if "plug" in intent:
            entities["device_type"] = "plug"

        intent_data["entities"] = entities

        log(
            f"🧩 Contexto aplicado -> intent={intent} | "
            f"location={entities.get('location')} | "
            f"device_type={entities.get('device_type')}"
        )

        return intent_data

    # ==================================================
    # PROCESSAR
    # ==================================================

    def processar(self, texto: str):
        texto = (texto or "").strip()

        if not texto:
            return {
                "text": "Não percebi o comando.",
                "end_conversation": True
            }

        if not self._contexto_valido():
            self._limpar_contexto()

        # confirmação pendente
        if self.pending_confirmation is not None:
            return self._responder_confirmacao(texto)

        # router base
        try:
            intent_data = self.router.detectar_intencao(texto)
        except Exception as e:
            log(f"❌ ERRO no IntentRouter: {e}")
            return None

        if not intent_data:
            return None

        # tenta resolver follow-up quando vier como chat
        intent_data = self._resolver_followup_incompleto(texto, intent_data)

        if intent_data.get("type") == "chat":
            return None

        # completa entidades com contexto recente
        intent_data = self._enriquecer_com_contexto(intent_data)

        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}
        requires_confirmation = bool(intent_data.get("requires_confirmation", False))

        log(
            f"🧠 Intent detetada -> intent={intent} | "
            f"entities={entities} | confirm={requires_confirmation}"
        )

        # confirmação
        if self._precisa_confirmacao(intent_data):
            self._guardar_confirmacao(intent_data)
            return {
                "text": self._texto_confirmacao(intent_data),
                "end_conversation": False
            }

        # execução local
        try:
            resposta = self.executor.executar(intent_data)
        except Exception as e:
            log(f"❌ ERRO no Executor: {e}")
            return {
                "text": "Ocorreu um erro ao executar o comando local.",
                "end_conversation": True
            }

        if resposta:
            self._atualizar_contexto(intent_data)
            return {
                "text": resposta,
                "end_conversation": False
            }

        return None