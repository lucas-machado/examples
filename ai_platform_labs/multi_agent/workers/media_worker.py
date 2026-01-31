import redis
import time
import json

import sys
import os

# Forçar stdout a não usar buffer para aparecer nos logs do Docker imediatamente
sys.stdout.reconfigure(line_buffering=True)

r = redis.from_url("redis://redis:6379/0")

def worker_loop(queue_name):
    print(f"[*] Worker iniciado na fila: {queue_name}")
    while True:
        # Bloqueia até chegar uma mensagem
        _, message = r.blpop(queue_name)
        task = json.loads(message)
        
        task_name = task.get('task')
        data = task.get('data', {})
        
        print(f"[Worker] Processando {task_name}...")
        
        if task_name == 'publish_content':
            topic = data.get('topic', 'N/A')
            content = data.get('content', 'No Content')
            print(f"\n========== [Worker] PUBLISHING CONTENT ({topic}) ==========")
            print(content)
            print("===========================================================\n")
        
        time.sleep(2) # Simula tarefa pesada
        print(f"[Worker] {task_name} concluído com sucesso!")

if __name__ == "__main__":
    import sys
    worker_loop(sys.argv[1])