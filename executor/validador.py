COMANDOS_PERMITIDOS = [
    "sistema",
    "codigo"
]


def validar_comando(comando: dict) -> bool:

    tipo = comando.get("tipo")

    if tipo not in COMANDOS_PERMITIDOS:
        return False

    return True