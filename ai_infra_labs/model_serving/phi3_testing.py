import requests

# Ajuste da URL para a porta padrão do Ollama
# O Ollama suporta a API da OpenAI no endpoint /v1
URL = "http://localhost:11434/v1/completions"

payload = {
    "model": "phi3", # Nome do modelo conforme carregado no Ollama
    "prompt": "Explique o que é fragmentação de memória para um arquiteto de software.",
    "max_tokens": 100,
    "temperature": 0.7
}

try:
    response = requests.post(URL, json=payload)
    response.raise_for_status()
    print(response.json()['choices'][0]['text'])
except requests.exceptions.ConnectionError:
    print("Erro: O servidor Ollama não foi encontrado. Certifique-se de que ele está ativo na porta 11434.")
except Exception as e:
    print(f"Erro inesperado: {e}")