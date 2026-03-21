# ==================================================
# 🧠 COMMAND VOCAB - JARVIS MK5
# ==================================================

LOCATION_ALIASES = {
    "wc": ["wc", "casa de banho", "banho"],
    "quarto": ["quarto", "meu quarto"],
    "sala": ["sala", "sala de estar"],
    "cozinha": ["cozinha"],
    "escritorio": ["escritorio", "escritório", "office"],
}

DEVICE_ALIASES = {
    "light": ["luz", "lampada", "lâmpada", "candeeiro", "candeeiro de teto"],
}

INTENT_PATTERNS = {
    "smart_home.light_on": [
        "liga",
        "acende",
        "turn on",
        "mete a luz",
    ],
    "smart_home.light_off": [
        "desliga",
        "apaga",
        "turn off",
        "mete as escuras",
        "mete às escuras",
    ],
    "smart_home.brightness_up": [
        "mais claro",
        "aumenta o brilho",
        "sobe o brilho",
        "mais luz",
    ],
    "smart_home.brightness_down": [
        "mais escuro",
        "baixa o brilho",
        "menos luz",
        "pouca luz",
    ],
    "smart_home.color_warmer": [
        "mais quente",
        "tom mais quente",
        "luz quente",
    ],
    "smart_home.color_cooler": [
        "mais fria",
        "tom mais frio",
        "luz fria",
    ],
    "smart_home.scene_cinema": [
        "modo cinema",
        "cinema",
        "ver filme",
    ],
    "smart_home.scene_relax": [
        "modo relax",
        "relax",
        "ambiente relax",
    ],
    "smart_home.scene_gaming": [
        "modo gaming",
        "gaming",
        "jogar",
    ],
}