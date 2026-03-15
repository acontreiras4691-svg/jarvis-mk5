import requests

url = "http://192.168.1.108:5000/comando"

dados = {
    "texto": "que horas são"
}

resposta = requests.post(url, json=dados)

print(resposta.json())