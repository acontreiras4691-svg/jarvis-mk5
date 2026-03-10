import requests

OLLAMA_URL = "http://192.168.1.108:11434/api/generate"

def perguntar_ia(pergunta):

    data = {
        "model": "llama3",
        "prompt": f"Responde sempre em português de Portugal. {pergunta}",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        resposta = response.json()["response"]
        return resposta.strip()

    except Exception as e:
        print("Erro IA:", e)
        return "Desculpa Dudu, não consegui ligar ao servidor de inteligência artificial."