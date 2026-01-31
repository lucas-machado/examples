import httpx
import redis
import json
import os
import sys
import logging

# Configuração de Logger para garantir output no Docker
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# DEBUG: Verificar chave de API
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"--- DEBUG INFO ---")
logger.info(f"Key present: {bool(api_key)}")
if api_key:
    logger.info(f"Key length: {len(api_key)}")
    logger.info(f"Key starts with: {api_key[:8]}...")
    logger.info(f"Key ends with: ...{api_key[-4:]}")
logger.info(f"------------------")

from fastapi import FastAPI
from typing import Annotated, Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, create_react_agent

# --- Configurações ---
app = FastAPI(title="Supervisor Agent (Intelligent)")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
RESEARCHER_URL = os.getenv("RESEARCHER_URL", "http://researcher-service:8001")
WRITER_URL = os.getenv("WRITER_URL", "http://writer-agent:8002")

# Setup Redis
try:
    r_client = redis.from_url(REDIS_URL)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    r_client = None

# --- Ferramentas (Tools) que o Supervisor pode usar ---

@tool
async def call_researcher_agent(query: str) -> str:
    """
    Use this tool to research information about a topic.
    It calls the Researcher Agent and returns the context found.
    """
    print(f"[Tool] Calling Researcher with query: {query}", flush=True)
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{RESEARCHER_URL}/search", json={"text": query}, timeout=30.0)
            res.raise_for_status()
            data = res.json().get("results", "No results found.")
            # Log parcial para não poluir
            print(f"[Tool] Researcher returned: {str(data)[:100]}...", flush=True) 
            return data
        except Exception as e:
            return f"Error calling researcher: {e}"

@tool
async def call_writer_agent(topic: str, context: str) -> str:
    """
    Use this tool to write the final content/article.
    You MUST provide the original topic and the context gathered from research.
    """
    print(f"[Tool] Calling Writer for topic: {topic}", flush=True)
    async with httpx.AsyncClient() as client:
        try:
            payload = {"topic": topic, "context": context}
            res = await client.post(f"{WRITER_URL}/write", json=payload, timeout=60.0)
            res.raise_for_status()
            return res.json().get("content", "Error generating content.")
        except Exception as e:
            return f"Error calling writer: {e}"

@tool
def publish_to_worker(topic: str, final_content: str) -> str:
    """
    Use this tool ONLY when the content is ready and finalized.
    It sends the work to the processing queue.
    """
    print(f"[Tool] Dispatching to Worker...", flush=True)
    if r_client:
        task = {
            "task": "publish_content",
            "data": {"topic": topic, "content": final_content}
        }
        r_client.rpush("media_queue", json.dumps(task))
        return "Successfully dispatched to worker queue."
    return "Failed to connect to Redis queue."

# Lista de ferramentas disponíveis para o LLM
tools = [call_researcher_agent, call_writer_agent, publish_to_worker]

# --- Configuração do Modelo (O Cérebro do Supervisor) ---
# O Supervisor precisa de uma LLM para decidir qual ferramenta usar
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # ou gpt-3.5-turbo
# Nota: create_react_agent faz o bind_tools automaticamente, não precisamos fazer aqui manualmente


from langgraph.prebuilt import create_react_agent

# ... (código anterior de tools e llm permanece igual) ...

# --- Definição do Grafo (LangGraph Moderno) ---

# Em vez de montar manualmente o StateGraph, usamos o create_react_agent
# que já configura o loop Supervisor -> Tools -> Supervisor corretamente.

system_prompt = """
You are the Supervisor of a content creation team.
Your goal is to create a high-quality article about the user's topic.

Follow this EXACT process:
1. CALL the Researcher Agent ONCE to gather information about the topic.
2. WAIT for the research results.
3. ANALYZE the results. Even if the information is brief, DO NOT search again. Use what you have.
4. CALL the Writer Agent passing the topic and the context found.
5. CALL the publish tool with the finalized content.
6. RESPOND to the user that the process is complete.

DO NOT loop or search repeatedly. Proceed to writing immediately after the first search.
"""

# O create_react_agent já faz o bind_tools internamente e gerencia o estado
# Nota: O parâmetro correto nesta versão é 'prompt'.
app_graph = create_react_agent(llm, tools, prompt=system_prompt)

# --- API Endpoints ---

@app.post("/run")
async def run_workflow(topic: str):
    logger.info(f"--- Iniciando Workflow para: {topic} ---")
    
    initial_state = {
        "messages": [HumanMessage(content=f"Please produce content about {topic}")]
    }
    
    # Executa o grafo e pega o último estado
    final_state = await app_graph.ainvoke(initial_state)
    
    # Pega a última mensagem do assistente
    last_msg = final_state["messages"][-1].content
    
    return {
        "status": "completed",
        "supervisor_response": last_msg
    }

@app.get("/health")
def health():
    return {"status": "ok"}
