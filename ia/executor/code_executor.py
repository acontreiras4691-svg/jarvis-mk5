from executor.acoes_sistema import executar_acao_sistema


def executar(comando: dict):

    intent = comando.get("intent")
    entities = comando.get("entities", {})

    # --------------------------------
    # COMANDOS DE SISTEMA
    # --------------------------------

    if intent == "COMANDO":

        acao = entities.get("acao")

        if acao:

            return executar_acao_sistema(entities)

    # --------------------------------
    # FACTUAL
    # --------------------------------

    if intent == "FACTUAL":
        return "Entendido."

    # --------------------------------
    # OUTROS
    # --------------------------------

    return None