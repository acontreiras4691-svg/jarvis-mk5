import chromadb
from sentence_transformers import SentenceTransformer
import os
import time
import re
from config.configuracoes import (
    CAMINHO_MEMORIA,
    MODELO_EMBEDDING,
    TOP_K_MEMORIA
)


class MemoriaRAG:

    def __init__(self):

        os.makedirs(CAMINHO_MEMORIA, exist_ok=True)

        self.client = chromadb.PersistentClient(path=CAMINHO_MEMORIA)

        self.collection = self.client.get_or_create_collection(
            name="jarvis_memoria"
        )

        self.encoder = SentenceTransformer(MODELO_EMBEDDING)

    # ==================================================
    # 🔹 UTILITÁRIOS
    # ==================================================

    def _normalizar(self, texto: str) -> str:
        texto = texto.lower().strip()
        texto = re.sub(r"[^\w\s]", "", texto)
        texto = re.sub(r"\s+", " ", texto)
        return texto

    def _gerar_id(self, texto: str) -> str:
        return str(abs(hash(self._normalizar(texto))))

    def _criar_metadata(self, prioridade: int) -> dict:
        return {
            "timestamp": time.time(),
            "prioridade": prioridade,
            "frequencia": 1,
            "notificado": False
        }

    # ==================================================
    # 🔹 GUARDAR FACTO
    # ==================================================

    def guardar_facto(self, texto: str, prioridade: int = 1):

        if not texto or len(texto.strip()) < 3:
            return

        texto = texto.strip()
        doc_id = self._gerar_id(texto)

        embedding = self.encoder.encode(texto).tolist()
        agora = time.time()

        try:
            existente = self.collection.get(ids=[doc_id])

            if existente and existente.get("ids"):
                meta_antiga = existente["metadatas"][0] or {}

                metadata = {
                    "timestamp": agora,
                    "prioridade": meta_antiga.get("prioridade", prioridade),
                    "frequencia": meta_antiga.get("frequencia", 1) + 1,
                    "notificado": meta_antiga.get("notificado", False)
                }
            else:
                metadata = self._criar_metadata(prioridade)

        except Exception:
            metadata = self._criar_metadata(prioridade)

        self.collection.upsert(
            documents=[texto],
            embeddings=[embedding],
            ids=[doc_id],
            metadatas=[metadata]
        )

    # ==================================================
    # 🔹 PESQUISA INTELIGENTE
    # ==================================================

    def pesquisar(self, pergunta: str, top_k: int = TOP_K_MEMORIA):

        if not pergunta:
            return []

        embedding = self.encoder.encode(pergunta).tolist()

        resultados = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        if not resultados.get("documents"):
            return []

        documentos = resultados["documents"][0]
        metadatas = resultados["metadatas"][0]

        agora = time.time()
        memorias_score = []

        for doc, meta in zip(documentos, metadatas):

            meta = meta or {}

            prioridade = meta.get("prioridade", 1)
            frequencia = meta.get("frequencia", 1)
            timestamp = meta.get("timestamp", agora)

            dias = (agora - timestamp) / 86400
            fator_recencia = 1 / (1 + dias)

            score = prioridade * frequencia * fator_recencia

            memorias_score.append((doc, score))

        memorias_score.sort(key=lambda x: x[1], reverse=True)

        return [m[0] for m in memorias_score]

    # ==================================================
    # 🔹 VERIFICAÇÃO PROATIVA
    # ==================================================

    def verificar_memorias_importantes(self):

        resultados = self.collection.get()

        if not resultados.get("documents"):
            return None

        agora = time.time()

        for doc, meta in zip(resultados["documents"], resultados["metadatas"]):

            meta = meta or {}

            prioridade = meta.get("prioridade", 1)
            timestamp = meta.get("timestamp", agora)
            notificado = meta.get("notificado", False)

            dias = (agora - timestamp) / 86400

            if prioridade >= 3 and dias < 2 and not notificado:

                meta["notificado"] = True

                self.collection.upsert(
                    documents=[doc],
                    embeddings=[self.encoder.encode(doc).tolist()],
                    ids=[self._gerar_id(doc)],
                    metadatas=[meta]
                )

                return doc

        return None