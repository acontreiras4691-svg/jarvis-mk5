import requests

def pesquisar_web(query):

    url = "https://duckduckgo.com/?q=" + query.replace(" ", "+")

    try:

        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            return f"Resultados encontrados para: {query}"

        return "Não consegui pesquisar na internet."

    except Exception as e:

        return f"Erro na pesquisa: {e}"