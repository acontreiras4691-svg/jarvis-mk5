from executor.acoes_sistema import executar_acao_sistema


def executar(comando: dict):

    tipo = comando.get("tipo")

    if tipo == "sistema":
        return executar_acao_sistema(comando)

    return "Tipo de comando desconhecido."