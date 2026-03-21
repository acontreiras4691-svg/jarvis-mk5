# ==================================================
# 🎩 PERSONALITY - JARVIS MK5
# ==================================================

import random


class JarvisPersonality:
    def __init__(self, user_name="Dudu"):
        self.user_name = user_name

    def pick(self, options):
        return random.choice(options)

    def _is_error_text(self, text: str | None) -> bool:
        if not text:
            return True

        text_norm = text.lower().strip()

        sinais_erro = [
            "não consegui",
            "nao consegui",
            "falha",
            "erro",
            "não percebi",
            "nao percebi",
            "não encontrei",
            "nao encontrei",
            "falta dizer",
            "inválido",
            "invalido",
            "ainda não está disponível",
            "ainda nao esta disponivel",
            "ainda não sei executar",
            "ainda nao sei executar",
            "check device key or version",
        ]

        return any(sinal in text_norm for sinal in sinais_erro)

    def success(self, intent: str, base_text: str, entities: dict | None = None) -> str:
        entities = entities or {}
        location = entities.get("location")
        app = entities.get("app")
        brilho = entities.get("brightness")

        # ------------------------------------------------
        # Se já veio erro do executor, respeitar o erro
        # ------------------------------------------------
        if self._is_error_text(base_text):
            return base_text

        # ------------------------------------------------
        # SMART HOME
        # ------------------------------------------------
        if intent == "smart_home.light_on":
            return self.pick([
                f"Pronto, {self.user_name}. Já tens luz{f' em {location}' if location else ''}.",
                f"Feito. Liguei a luz{f' em {location}' if location else ''}.",
                f"Está ligado{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_off":
            return self.pick([
                f"Pronto. Apaguei a luz{f' em {location}' if location else ''}.",
                f"Feito, {self.user_name}. Agora ficou tudo mais escuro{f' em {location}' if location else ''}.",
                f"Já está. Luz desligada{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_set_brightness":
            return self.pick([
                f"Feito. Ajustei o brilho para {brilho}%{f' em {location}' if location else ''}.",
                f"Pronto, {self.user_name}. O brilho ficou nos {brilho}%{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_brightness_up":
            return self.pick([
                f"Feito. Dei mais luz{f' em {location}' if location else ''}.",
                f"Pronto. Agora está mais claro{f' em {location}' if location else ''}.",
                f"Aumentei a luminosidade{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_brightness_down":
            return self.pick([
                f"Feito. Baixei a intensidade{f' em {location}' if location else ''}.",
                f"Pronto. Agora tens uma luz mais suave{f' em {location}' if location else ''}.",
                f"Reduzi o brilho{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_warmer":
            return self.pick([
                f"Feito. Dei um tom mais quente à luz{f' em {location}' if location else ''}.",
                f"Pronto, {self.user_name}. Agora está mais acolhedor{f' em {location}' if location else ''}.",
                f"A luz ficou mais quente{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.light_cooler":
            return self.pick([
                f"Feito. Ajustei a luz para um tom mais frio{f' em {location}' if location else ''}.",
                f"Pronto. Agora a luz está mais fria{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.scene_relax":
            return self.pick([
                f"Pronto, {self.user_name}. Deixei um ambiente mais relaxado{f' em {location}' if location else ''}.",
                f"Feito. Modo relax ativo{f' em {location}' if location else ''}.",
                f"Já está. O ambiente ficou mais suave{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.scene_cinema":
            return self.pick([
                f"Pronto, {self.user_name}. Ambiente de cinema ligado{f' em {location}' if location else ''}.",
                f"Feito. Modo cinema ativado{f' em {location}' if location else ''}.",
                f"Já está. Ficou tudo pronto para ver alguma coisa{f' em {location}' if location else ''}.",
            ])

        if intent == "smart_home.scene_gaming":
            return self.pick([
                f"Pronto, {self.user_name}. Ambiente de jogo preparado{f' em {location}' if location else ''}.",
                f"Feito. Modo gaming ativado{f' em {location}' if location else ''}.",
                f"Já está. Setup mais virado para jogo{f' em {location}' if location else ''}.",
            ])

        # ------------------------------------------------
        # APPS
        # ------------------------------------------------
        if intent == "system.open_app":
            nome_app = app.capitalize() if app else "a aplicação"

            if base_text == "OK_APP_OPEN":
                return self.pick([
                    f"Já trato disso. A abrir {nome_app}.",
                    f"Feito, {self.user_name}. Vou abrir {nome_app}.",
                    f"Pronto. {nome_app} a arrancar.",
                ])

            return base_text

        # ------------------------------------------------
        # SISTEMA
        # ------------------------------------------------
        if intent == "system.shutdown":
            return self.pick([
                f"Entendido, {self.user_name}. Vou desligar o computador em 5 segundos.",
                "Tudo certo. O computador vai desligar dentro de momentos.",
            ])

        if intent == "system.restart":
            return self.pick([
                f"Entendido, {self.user_name}. Vou reiniciar o computador em 5 segundos.",
                "Tudo certo. O sistema vai reiniciar dentro de momentos.",
            ])

        # ------------------------------------------------
        # ASSISTANT
        # ------------------------------------------------
        if intent == "assistant.greeting":
            return self.pick([
                f"Olá, {self.user_name}. Estou online.",
                f"Boa, {self.user_name}. Tudo operacional.",
                f"Olá, {self.user_name}. Pronto para ajudar.",
            ])

        if intent == "assistant.thanks":
            return self.pick([
                "Sempre às ordens.",
                f"De nada, {self.user_name}.",
                "Sem problema.",
            ])

        if intent == "assistant.goodbye":
            return self.pick([
                f"Até já, {self.user_name}.",
                "Até logo.",
                "Fico por aqui.",
            ])

        if intent in ["assistant.time", "assistant.date"]:
            return base_text

        return base_text

    def failure(self, intent: str | None = None) -> str:
        return self.pick([
            f"Não consegui executar isso, {self.user_name}.",
            "Tentei tratar disso, mas algo falhou.",
            "Ainda não consegui concluir esse pedido.",
        ])

    def unknown(self) -> str:
        return self.pick([
            "Não percebi totalmente esse pedido.",
            f"Não apanhei bem isso, {self.user_name}.",
            "Podes reformular esse comando?",
        ])