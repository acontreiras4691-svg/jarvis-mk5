# core/orchestrator.py

class Orchestrator:

    def __init__(self, brain, executor):
        self.brain = brain
        self.executor = executor

    def processar(self, texto):

        # 1. perceber intenção
        intent = self.brain.detectar_intencao(texto)

        # 2. decidir ação
        plano = self.brain.criar_plano(intent, texto)

        # 3. executar ação
        resultado = self.executor.executar(plano)

        return resultado