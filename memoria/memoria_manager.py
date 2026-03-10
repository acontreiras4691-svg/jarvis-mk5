import json
import os
from core.logger import log

CAMINHO_MEMORIA = "dados/memoria.json"

class MemoriaManager:
    def __init__(self):
        os.makedirs("dados", exist_ok=True)
        if not os.path.exists(CAMINHO_MEMORIA):
            self.resetar_memoria()

    def resetar_memoria(self):
        with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump({
                "historico_conversa": [],
                "preferencias": {},
                "ultimo_comando": ""
            }, f, indent=4, ensure_ascii=False)

    def carregar(self):
        try:
            with open(CAMINHO_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.resetar_memoria()
            return self.carregar()

    def guardar(self, dados):
        with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    # 🎯 CORREÇÃO: Agora aceita o dicionário {"role": "...", "content": "..."}
    def adicionar_historico(self, mensagem_dict):
        dados = self.carregar()
        dados["historico_conversa"].append(mensagem_dict)
        
        # Mantém apenas as últimas 10 interações para não estourar o limite da IA
        if len(dados["historico_conversa"]) > 10:
            dados["historico_conversa"].pop(0)
            
        self.guardar(dados)
        log(f"🧠 Memória atualizada: {mensagem_dict.get('role')}")

    # 🚀 O MÉTODO QUE FALTA: Resolve o erro de AttributeError
    def obter_historico_curto(self):
        dados = self.carregar()
        return dados.get("historico_conversa", [])

    def atualizar_ultimo_comando(self, comando):
        dados = self.carregar()
        dados["ultimo_comando"] = comando
        self.guardar(dados)