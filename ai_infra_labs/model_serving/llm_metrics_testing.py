import requests
import time
import json

def test_llm_latency(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": True # Essencial para medir TTFT
    }

    start_time = time.time()
    first_token_time = None
    tokens_count = 0

    response = requests.post(url, json=data, stream=True)
    
    for line in response.iter_lines():
        if line:
            if first_token_time is None:
                first_token_time = time.time() # TTFT capturado aqui
            
            tokens_count += 1
            # Opcional: print(json.loads(line)['response'], end="", flush=True)

    end_time = time.time()
    
    ttft = (first_token_time - start_time) * 1000
    total_time = (end_time - start_time)
    tpot = (total_time / tokens_count) * 1000 if tokens_count > 0 else 0

    print(f"\n\n--- Métricas de Infraestrutura ---")
    print(f"TTFT (Time to First Token): {ttft:.2f} ms")
    print(f"TPOT (Time Per Output Token): {tpot:.2f} ms")
    print(f"Tokens/seg: {1000/tpot:.2f}")

test_llm_latency("Explique o conceito de PagedAttention.")