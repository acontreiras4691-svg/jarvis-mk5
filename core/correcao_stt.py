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

        # brilho / intensidade
        "metaluz": "mete a luz",
        "meta-luz": "mete a luz",
        "meta": "mete",
        "metalu": "mete a luz",

        # quarto
        "quad": "quarto",
        "quart": "quarto",
        "quartoo": "quarto",
        "quarto.": "quarto",

        # sala
        "salaa": "sala",
        "sala.": "sala",

        # wc
        "wc.": "wc",

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

    # casa de banho -> wc
    texto = texto.replace("casa de banho", "wc")
    texto = texto.replace("casa banho", "wc")
    texto = texto.replace("na casa de banho", "no wc")
    texto = texto.replace("no casa de banho", "no wc")
    texto = texto.replace("na casa banho", "no wc")

    # limpar duplicações
    texto = texto.replace("wc wc", "wc")

    # meta-luz / mete a luz
    texto = texto.replace("meta luz", "mete a luz")
    texto = texto.replace("meta-luz", "mete a luz")
    texto = texto.replace("metaluz", "mete a luz")

    # metade -> 50% (ajuda o router de brilho)
    texto = texto.replace("a metade", "50%")
    texto = texto.replace("para metade", "para 50%")
    texto = texto.replace("metade", "50%")

    # frases comuns de brilho
    texto = texto.replace("baixa a luz para 50%", "mete a luz para 50%")
    texto = texto.replace("abaixo a luz para 50%", "mete a luz para 50%")
    texto = texto.replace("baixa a luz do wc para 50%", "mete a luz no wc para 50%")
    texto = texto.replace("baixa a luz do quarto para 50%", "mete a luz no quarto para 50%")

    # limpeza leve
    texto = " ".join(texto.split())
    texto = texto.strip()

    return texto