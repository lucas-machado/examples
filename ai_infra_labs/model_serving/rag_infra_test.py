import chromadb
from chromadb.utils import embedding_functions
import ollama

# 1. Configurar o Banco Vetorial (Local)
client = chromadb.Client()
# Usaremos um modelo de embedding padrão do mercado
emb_fn = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="startup_docs", embedding_function=emb_fn)

# 2. "Ensinar" o banco (Ingestão de Dados)
# Imagine que estes são documentos privados da sua empresa
collection.add(
    documents=[
        "A política de reembolso da nossa startup permite devoluções em até 30 dias.",
        "O servidor de produção deve ser reiniciado apenas aos domingos às 03:00.",
        "O CTO definiu que usaremos vLLM para escalar nossos modelos."
    ],
    ids=["doc1", "doc2", "doc3"]
)

# 3. A Busca Semântica
query = "Qual a regra para o servidor de produção?"
results = collection.query(query_texts=[query], n_results=1)
contexto = results['documents'][0][0]

print(f"Trecho encontrado no banco: {contexto}\n")

# 4. A Geração Aumentada (RAG)
prompt = f"""
Use apenas o contexto abaixo para responder à pergunta.
Contexto: {contexto}
Pergunta: {query}
"""

response = ollama.generate(model='llama3:8b', prompt=prompt)
print(f"Resposta do LLM com RAG: {response['response']}")