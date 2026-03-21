import os
import zipfile
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------

JARVIS_PATH = r"C:\Jarvis\Jarvis Final"
BACKUP_PATH = r"C:\Jarvis\Backups"

MAX_BACKUPS = 10


# -----------------------------
# CRIAR BACKUP
# -----------------------------

def criar_backup():

    os.makedirs(BACKUP_PATH, exist_ok=True)

    data = datetime.now().strftime("%Y-%m-%d_%H-%M")

    nome_backup = f"jarvis_backup_{data}.zip"

    caminho_backup = os.path.join(BACKUP_PATH, nome_backup)

    print("Criando backup...")

    with zipfile.ZipFile(caminho_backup, "w", zipfile.ZIP_DEFLATED) as zipf:

        for root, dirs, files in os.walk(JARVIS_PATH):

            for file in files:

                caminho_completo = os.path.join(root, file)

                caminho_relativo = os.path.relpath(
                    caminho_completo,
                    JARVIS_PATH
                )

                zipf.write(
                    caminho_completo,
                    caminho_relativo
                )

    print("Backup criado:", caminho_backup)


# -----------------------------
# LIMPAR BACKUPS ANTIGOS
# -----------------------------

def limpar_backups():

    arquivos = sorted(
        os.listdir(BACKUP_PATH)
    )

    if len(arquivos) <= MAX_BACKUPS:
        return

    remover = arquivos[:-MAX_BACKUPS]

    for f in remover:

        caminho = os.path.join(BACKUP_PATH, f)

        os.remove(caminho)

        print("Backup removido:", f)


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    criar_backup()

    limpar_backups()

    print("Backup concluído.")