# ==================================================
# 🗣️ RESPONSE BUILDER - JARVIS MK5
# ==================================================

from assistant.personality import JarvisPersonality


class ResponseBuilder:
    def __init__(self, user_name="Dudu"):
        self.personality = JarvisPersonality(user_name=user_name)

    def build(self, intent_data: dict, executor_response: str | None) -> str:
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {}) or {}

        if intent == "assistant.chat":
            return self.personality.unknown()

        if not executor_response:
            return self.personality.failure(intent)

        return self.personality.success(
            intent=intent,
            base_text=executor_response,
            entities=entities,
        )