import re


WAKE_WORDS = {
    "jarvis",
    "javis",
    "jarviz",
    "jarves",
    "jarviss",
    "jarv",
    "jarvix",
    "jarveis",
    "gervais",
    "gerveis"
}


def ativado(texto: str) -> bool:

    if not texto:
        return False

    texto = texto.lower().strip()

    # remover pontuação
    texto = re.sub(r"[^\w\s]", "", texto)

    palavras = texto.split()

    if not palavras:
        return False

    for palavra in palavras:

        if palavra in WAKE_WORDS:
            return True

    return False