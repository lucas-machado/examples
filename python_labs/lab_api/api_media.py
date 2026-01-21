from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl, Field
import asyncio
import time
import structlog

# Configuração do structlog para saída JSON no terminal
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
app = FastAPI(title="Media Automation API")

class VideoTask(BaseModel):
    video_id: str
    video_url: HttpUrl
    duration: int = Field(..., ge=1, le=3600)

async def simulate_ai_processing(video_id: str):
    log = logger.bind(video_id=video_id, component="ai_worker")

    # Aqui simulamos o "Span" do OpenTelemetry
    start_time = time.time()
    log.info("🚀 [TRACE START] Processando vídeo", video_id=video_id)
    
    await asyncio.sleep(2) # Simula a chamada de IA
    
    end_time = time.time()
    log.info("✅ [TRACE END] Vídeo processado", video_id=video_id, duration=end_time - start_time)

@app.post("/v1/process", status_code=202)
async def process_media(task: VideoTask, background_tasks: BackgroundTasks):
    # O Pydantic já validou o 'task' automaticamente aqui!
    
    # Adicionamos a tarefa para rodar depois que a resposta for enviada (Background)
    background_tasks.add_task(simulate_ai_processing, task.video_id)
    
    return {"message": "Tarefa aceita e enviada para processamento", "task_id": task.video_id}