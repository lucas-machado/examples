# AI Multi-Agent Lab

Um laboratório completo de arquitetura multi-agente usando Docker, FastAPI, LangGraph e Redis.

## Arquitetura

1.  **Supervisor (Porta 8000)**: O cérebro. Usa LangGraph para orquestrar o fluxo.
2.  **Researcher (Porta 8001)**: Agente especialista em busca híbrida (Vetorial + Keywords).
3.  **Writer (Porta 8002)**: Agente especialista em escrita (LLM).
4.  **Worker**: Consumidor de fila Redis para tarefas assíncronas.
5.  **Redis**: Broker de mensagens.

## Como Rodar

1.  **Configuração de Ambiente**:
    Crie um arquivo `.env` na pasta `multi_agent` com sua chave da OpenAI:
    ```bash
    OPENAI_API_KEY=sk-...
    ```

2.  **Subir o Lab**:
    ```bash
    docker-compose up --build
    ```

3.  **Testar**:
    Envie uma requisição para o Supervisor:

    ```bash
    curl -X POST "http://localhost:8000/run?topic=LangGraph"
    ```

## O que acontece por baixo dos panos?

1.  O **Supervisor** recebe o request.
2.  Chama o **Researcher** para buscar contexto sobre "LangGraph".
3.  O **Researcher** busca na sua base de conhecimento (in-memory) e retorna resultados.
4.  O **Supervisor** passa o contexto para o **Writer**.
5.  O **Writer** gera um parágrafo resumido.
6.  O **Supervisor** envia o texto final para a fila `media_queue` no Redis.
7.  O **Worker** pega a mensagem e processa (printa no log).
