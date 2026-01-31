from fastapi import FastAPI
from pydantic import BaseModel
from hybrid_search import RetrievalPlatform

app = FastAPI(title="Researcher Service")

# Initialize Search Engine
platform = RetrievalPlatform()

# Populate with dummy data on startup
def populate_knowledge_base():
    print("[Researcher] Initializing knowledge base...")
    collection_name = "knowledge_base"
    platform.create_collection(collection_name)
    
    docs = [
        "Artificial Intelligence in 2025 is focused on agentic workflows where LLMs can take actions.",
        "The best way to cook pasta is to salt the water heavily, like the ocean.",
        "Docker Compose allows you to define and run multi-container Docker applications.",
        "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        "Python 3.11 introduced significant performance improvements over previous versions.",
        "Multi-agent systems consist of autonomous agents interacting to solve complex problems."
    ]
    
    platform.ingest(collection_name, docs)

populate_knowledge_base()

class Query(BaseModel):
    text: str

@app.post("/search")
async def search(query: Query):
    print(f"[Researcher] Searching for: {query.text}")
    
    results = platform.hybrid_search(query.text, "knowledge_base")
    
    if not results:
        return {"results": "No relevant information found."}
        
    # Extrai o texto e converte para string
    context_list = [r[0].payload['text'] for r in results]
    context = "\n---\n".join(context_list)
    
    # DEBUG: Imprimir o que está sendo retornado
    print(f"[Researcher] Returning context length: {len(context)}")
    
    return {"results": context}

@app.get("/health")
def health():
    return {"status": "ok"}
