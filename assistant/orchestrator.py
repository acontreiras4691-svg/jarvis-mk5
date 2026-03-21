# ==================================================
# 🧠 ORCHESTRATOR - JARVIS MK5
# ==================================================

from brain.intent_router import IntentRouter
from brain.context_manager import ContextManager
from executor.executor_engine import Executor
from assistant.response_builder import ResponseBuilder


class JarvisOrchestrator:
    def __init__(self, smart_home=None, user_name="Dudu"):
        self.router = IntentRouter()
        self.context = ContextManager()
        self.executor = Executor(smart_home=smart_home)
        self.response_builder = ResponseBuilder(user_name=user_name)

    # ------------------------------------------------

    def _is_smart_home_intent(self, intent: str | None) -> bool:
        return bool(intent and intent.startswith("smart_home."))

    def _filtrar_contexto_smart_home(self, entities: dict) -> dict:
        if not entities:
            return {}

        permitidas = {
            "location",
            "device_type",
        }

        filtradas = {}
        for chave, valor in entities.items():
            if chave in permitidas and valor is not None:
                filtradas[chave] = valor

        return filtradas

    # ------------------------------------------------

    def process_text(self, texto: str) -> dict:
        texto = (texto or "").strip()

        if not texto:
            return {
                "ok": False,
                "text": "Não disseste nada.",
                "intent": None,
                "entities": {},
            }

        # 1) detetar intenção
        intent_data = self.router.detectar_intencao(texto)

        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        print(
            f"🧠 Intent detetada -> intent={intent} | entities={entities} | "
            f"confirm={intent_data.get('requires_confirmation', False)}"
        )

        # 2) aplicar contexto APENAS a smart home
        if self._is_smart_home_intent(intent):
            entities_enriched = self.context.enrich(entities)
            intent_data["entities"] = entities_enriched

            print(
                f"🧩 Contexto aplicado -> intent={intent} | "
                f"location={entities_enriched.get('location')} | "
                f"device_type={entities_enriched.get('device_type')}"
            )

        # 3) tratar chat simples sem passar pelo executor
        if intent in {
            "assistant.chat",
            "assistant.greeting",
            "assistant.thanks",
            "assistant.goodbye",
        }:
            if intent == "assistant.chat":
                resposta_final = self.response_builder.personality.unknown()
            else:
                resposta_final = self.response_builder.build(intent_data, "ok")

            return {
                "ok": True,
                "text": resposta_final,
                "intent": intent,
                "entities": entities,
            }

        # 4) executar
        resposta_executor = self.executor.executar(intent_data)

        # 5) atualizar contexto só para smart home
        if self._is_smart_home_intent(intent):
            contexto_filtrado = self._filtrar_contexto_smart_home(
                intent_data.get("entities", {})
            )
            self.context.update(contexto_filtrado)
            dump = self.context.dump()

            print(
                f"🧠 Contexto atualizado -> location={dump.get('location')} | "
                f"device_type={dump.get('device_type')} | "
                f"intent={intent}"
            )

        # 6) construir resposta final com personalidade
        resposta_final = self.response_builder.build(intent_data, resposta_executor)

        # 7) garantir resposta segura
        if not resposta_final:
            resposta_final = "Não consegui gerar resposta para esse comando."

        return {
            "ok": True,
            "text": resposta_final,
            "intent": intent,
            "entities": intent_data.get("entities", {}),
        }