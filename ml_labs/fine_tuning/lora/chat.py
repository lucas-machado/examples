import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# --- CONFIGURAÇÕES ---
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_DIR = "qwen-insurance-en" # A pasta que seu script acabou de criar

print(">>> Inicializando o Corretor de Seguros AI...")

# 1. Carrega Tokenizer (Modo Inferência)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

# 2. Carrega Modelo Base
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto", # Usa MPS automaticamente
    trust_remote_code=True
)

# 3. Acopla o seu Fine-Tuning
print(f">>> Carregando adaptador: {ADAPTER_DIR}...")
try:
    model = PeftModel.from_pretrained(base_model, ADAPTER_DIR)
    model.eval() # Modo de produção
    print(">>> Sucesso! O modelo está pronto.")
except:
    print(">>> ERRO: Não achei o adaptador. Rode o treino primeiro!")
    exit()

print("\n" + "="*50)
print("🤖 INSURANCE BOT (Digite 'sair' para fechar)")
print("="*50)

# Loop de Chat
history = [] 
while True:
    user_input = input("\You: ")
    if user_input.lower() in ["sair", "exit", "quit"]:
        break
    
    # Monta o prompt com histórico simples (apenas última rodada para economizar memória)
    messages = [
        {"role": "system", "content": "You are a senior insurance expert. Be concise and technical."},
        {"role": "user", "content": user_input}
    ]
    
    # Formata e Tokeniza
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(base_model.device)
    
    # Gera
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.3,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decodifica apenas a resposta nova
    response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    
    print(f"Bot: {response}")