from assistant.orchestrator import JarvisOrchestrator

jarvis = JarvisOrchestrator()

while True:
    txt = input("Tu: ")

    if txt == "sair":
        break

    resposta = jarvis.process_text(txt)

    print("Jarvis:", resposta["text"])