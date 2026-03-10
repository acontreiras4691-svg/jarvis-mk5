import traceback
from core.logger import log


def executar_codigo_controlado(codigo: str):

    log("Execução de código iniciada.")

    ambiente_controlado = {}

    try:
        exec(codigo, {"__builtins__": {}}, ambiente_controlado)
        log("Execução de código concluída.")
        return "Código executado com sucesso."

    except Exception as e:
        erro = traceback.format_exc()
        log(f"Erro na execução de código: {erro}")
        return "Erro ao executar código."