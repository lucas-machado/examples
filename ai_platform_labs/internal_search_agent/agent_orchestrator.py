import sys
import os
import operator
from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from langgraph.prebuilt import ToolNode, tools_condition

# Adiciona o diretório raiz 'snippets' ao caminho de busca do Python
# __file__ é o arquivo atual. dirname sobe para 'agentic_platform'.
# O segundo dirname sobe para 'ai_platform_labs'.
# O terceiro dirname sobe para 'snippets'.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Agora a importação funcionará perfeitamente
from ai_platform_labs.hybrid_search.hybrid_search import RetrievalPlatform


class SearchInput(BaseModel):
    query: str = Field(description="The query to search the startup docs for.")


class StartupSearchTool(BaseTool):
    name: str = "search_startup_docs"
    description: str = "Search the startup docs for the given query."
    args_schema: Type[BaseModel] = SearchInput

    _platform: RetrievalPlatform = RetrievalPlatform()

    def __init__(self, platform: RetrievalPlatform, **kwargs):
        super().__init__(**kwargs)
        self._platform = platform

    def _run(self, query: str) -> str:
        print(f"\n   [System] 🔍 Executando busca no banco vetorial para: '{query}'...")

        search_results = self._platform.hybrid_search(query, "startup_docs")

        if not search_results:
            return "No information found in the internal docs."

        context = "\n".join([r[0].payload['text'] for r in search_results])
        content = f"I found this information in the internal docs:\n{context}"
        return content



# --- Definição do Estado do Agente ---
class AgentState(TypedDict):
    # O histórico de mensagens permite ao agente ter "memória"
    messages: Annotated[List[BaseMessage], operator.add]
    

# --- O Nó de Decisão (O "Cérebro") ---
class AgentOrchestrator:
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

    def call_model(self, state: AgentState):
        """Decide se responde diretamente ou se usa a ferramenta de busca."""
        
        print(f"\n🤖 [Agente] Pensando...")

        messages = state['messages']
        response = self.llm.invoke(messages)

        if response.tool_calls:
            print(f"👉 [Decisão] O Agente decidiu USAR FERRAMENTA!")
            for tool in response.tool_calls:
                print(f"   -> Ferramenta: {tool['name']}")
                print(f"   -> Args: {tool['args']}")
        else:
            print(f"👉 [Decisão] O Agente decidiu RESPONDER DIRETO.")

        return {"messages": [response]}

# --- Construção do Grafo (Infrastructure) ---
def create_agent_graph(orchestrator):
    workflow = StateGraph(AgentState)

    # Definimos os nós (as funções que criamos)
    workflow.add_node("agent", orchestrator.call_model)
    workflow.add_node("tools", ToolNode(tools=orchestrator.tools))

    # Definimos as arestas (fluxo de execução)
    workflow.set_entry_point("agent")
    
    # O conditional edge lê o output do 'agent' e decide para onde ir
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# --- Execução do Desafio ---
if __name__ == "__main__":
    # 1. Inicia sua plataforma do Lab 1
    platform = RetrievalPlatform()
    
    documents = [
        "Our startup's refund policy allows for returns within 30 days.",
        "The production server must be restarted only on Sundays at 03:00.",
        "The CTO has determined that we will use vLLM to scale our models."
    ]

    platform.create_collection("startup_docs")
    platform.ingest("startup_docs", documents)

    search_tool = StartupSearchTool(platform=platform)


    orchestrator = AgentOrchestrator(tools=[search_tool])


    app = create_agent_graph(orchestrator)
    

    inputs = {"messages": [HumanMessage(content="What is our policy for Sunday server restarts?")]}
    for output in app.stream(inputs):
        print(output)