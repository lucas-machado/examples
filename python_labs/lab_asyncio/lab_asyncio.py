import asyncio
import random
from typing import Dict, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator
from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.parse import urlparse
from typing import Any

# --- DESAFIO 1: DEFINIR O MODELO ---
class VideoTask(BaseModel):
    video_id: str
    video_url: HttpUrl
    duration: int = Field(..., ge=1, le=3600)
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('video_url')
    @classmethod
    def validate_s3_url(cls, v: HttpUrl) -> HttpUrl:
        # No Pydantic V2, HttpUrl tem o atributo .host
        allowed_hosts = ['s3.amazonaws.com', 'storage.googleapis.com']
        
        # Verificamos se o host da URL está na nossa lista permitida
        if v.host not in allowed_hosts:
            raise ValueError(f"Domínio '{v.host}' não permitido. Use apenas S3 ou GCS.")
        return v

# --- DESAFIO 2: CHAMADA COM RETRY ---
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def call_transcription_ai(video_id: str):
    print(f"🔄 Tentando transcrever {video_id}...")
    if random.random() < 0.5: # 50% de chance de erro
        raise Exception("Serviço de IA instável")
    await asyncio.sleep(0.5)
    return f"Transcrição de {video_id} concluída!"

# --- DESAFIO 3: O ORQUESTRADOR ---
async def main():
    tasks_data = [
        {"video_id": "v1", "video_url": "https://s3.amazonaws.com/clip1.mp4", "duration": 120},
        {"video_id": "v2", "video_url": "https://storage.googleapis.com/clip2.mp4", "duration": 45},
        # {"video_id": "v3", "video_url": "https://youtube.com/watch?v=123", "duration": 60},
    ]

    try:
        tasks = [VideoTask(**task) for task in tasks_data]
    except Exception as e:
        print(f"Erro de validação: {e}")
        return

    results = await asyncio.gather(*[call_transcription_ai(task.video_id) for task in tasks],
                                   return_exceptions=True)

    print("\n✅ Resultados Finais:")
    for task, res in zip(tasks, results):
        if isinstance(res, Exception):
            # Aqui você logaria no Sentry ou Datadog
            print(f"❌ Vídeo {task.video_id} FALHOU: {res}")
        else:
            print(f"✅ Vídeo {task.video_id} CONCLUÍDO: {res}")

if __name__ == "__main__":
    asyncio.run(main())