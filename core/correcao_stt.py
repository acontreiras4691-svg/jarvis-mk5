# ==================================================
# 🔧 CORREÇÃO DE ERROS DO STT
# ==================================================

import unicodedata


# ==================================================
# NORMALIZAR TEXTO
# ==================================================

def normalizar(texto: str) -> str:
    """
    Remove acentos para facilitar matching.
    """

    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


# ==================================================
# CORRIGIR TEXTO DO STT
# ==================================================

def corrigir_texto_stt(texto: str) -> str:

    texto = texto.lower()
    texto = normalizar(texto)

    # ------------------------------------------------
    # CORREÇÕES DIRETAS
    # ------------------------------------------------

    correcoes = {

        # wakeword
        "jarvas": "jarvis",
        "jalves": "jarvis",
        "javis": "jarvis",

        # erros comuns whisper
        "inna": "na",
        "ina": "na",
        "noo": "no",

        # luz
        "descende": "acende",
        "desende": "acende",
        "ascende": "acende",

        # quarto
        "quad": "quarto",
        "quart": "quarto",
        "quartoo": "quarto",
        "quarto.": "quarto",

        # sala
        "salaa": "sala",
        "sa": "sala",
        "sala.": "sala",

        # wc
        "wc.": "wc",
        "banho": "wc",
        "casa": "wc",

        # casa de banho
        "casa banho": "wc",
        "casa de banho": "wc",

        # luz
        "luzes": "luz",
        "luze": "luz",

        # tomada
        "tomadas": "tomada",

        # apps comuns
        "youtub": "youtube",
        "yutube": "youtube",
        "spotfy": "spotify",
        "discor": "discord",
    }

    # ------------------------------------------------
    # SUBSTITUIR PALAVRAS
    # ------------------------------------------------

    palavras = texto.split()

    palavras_corrigidas = []

    for p in palavras:

        if p in correcoes:
            palavras_corrigidas.append(correcoes[p])
        else:
            palavras_corrigidas.append(p)

    texto = " ".join(palavras_corrigidas)

    # ------------------------------------------------
    # CORREÇÕES DE EXPRESSÃO
    # ------------------------------------------------

    if "casa de banho" in texto:
        texto = texto.replace("casa de banho", "wc")

    if "casa banho" in texto:
        texto = texto.replace("casa banho", "wc")

    if "na casa de banho" in texto:
        texto = texto.replace("na casa de banho", "no wc")

    if "no casa de banho" in texto:
        texto = texto.replace("no casa de banho", "no wc")

    if "na casa banho" in texto:
        texto = texto.replace("na casa banho", "no wc")

    if "luz no wc wc" in texto:
        texto = texto.replace("wc wc", "wc")

    # ------------------------------------------------
    # LIMPEZA FINAL
    # ------------------------------------------------

    texto = texto.strip()

    return texto