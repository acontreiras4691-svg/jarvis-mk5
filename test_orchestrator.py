from assistant.orchestrator import JarvisOrchestrator
from smart_home.smart_home_manager import SmartHomeManager


def main():
    smart_home = SmartHomeManager()
    jarvis = JarvisOrchestrator(smart_home=smart_home, user_name="Dudu")

    while True:
        txt = input("Tu: ").strip()

        if txt.lower() in {"sair", "exit"}:
            break

        resposta = jarvis.process_text(txt)
        print("Jarvis:", resposta["text"])


if __name__ == "__main__":
    main()