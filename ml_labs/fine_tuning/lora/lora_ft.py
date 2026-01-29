import torch
import os
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, PeftModel
from trl import SFTTrainer, SFTConfig

# ==========================================
# CONFIGURAÇÕES DO LAB (Edite aqui)
# ==========================================
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct" 
OUTPUT_DIR = "qwen-insurance-en"
DATASET_FILE = "insurance_dataset.jsonl"
MAX_STEPS = 60
LEARNING_RATE = 2e-5

# Configuração de Hardware (Mac/MPS)
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"✅ Hardware detectado: {device.upper()}")

# ==========================================
# 1. CARREGAMENTO DE DADOS
# ==========================================
print(f"📂 Carregando dataset: {DATASET_FILE}...")
try:
    dataset = load_dataset("json", data_files=DATASET_FILE, split="train")
except Exception as e:
    print(f"❌ Erro ao ler dataset: {e}")
    exit()

# ==========================================
# 2. PREPARAÇÃO DO MODELO
# ==========================================
print("🧠 Carregando Qwen2.5-3B...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token 
tokenizer.padding_side = "right" # Importante: Para treino, padding é à direita

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16, 
    device_map=device,
    trust_remote_code=True
)

peft_config = LoraConfig(
    r=16, 
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"], 
    bias="none",
    task_type="CAUSAL_LM"
)

# ==========================================
# 3. FORMATAÇÃO (Chat Template)
# ==========================================
def format_prompt(sample):
    is_batch = isinstance(sample['instruction'], list)
    prompts = []
    
    instructions = sample['instruction'] if is_batch else [sample['instruction']]
    contexts = sample['context'] if is_batch else [sample['context']]
    responses = sample['response'] if is_batch else [sample['response']]

    for i in range(len(instructions)):
        messages = [
            {"role": "system", "content": f"You are an insurance expert. Context: {contexts[i]}"},
            {"role": "user", "content": instructions[i]},
            {"role": "assistant", "content": responses[i]}
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        prompts.append(text)
    
    return prompts if is_batch else prompts[0]

# ==========================================
# 4. TREINAMENTO
# ==========================================
print("🏋️‍♂️ Iniciando Treinamento...")

training_args = SFTConfig(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8, 
    max_steps=MAX_STEPS,
    learning_rate=LEARNING_RATE, 
    logging_steps=5,
    optim="adamw_torch",
    fp16=True,
    save_strategy="no",      # Não salvamos checkpoints intermediários para poupar disco
    report_to="none",
    dataset_text_field="text",
    packing=False
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    formatting_func=format_prompt,
    args=training_args,
    processing_class=tokenizer
)

trainer.train()

# ==========================================
# 5. SALVAMENTO (CRÍTICO PARA REUSO)
# ==========================================
print("💾 Salvando o adaptador treinado...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Modelo salvo em: ./{OUTPUT_DIR}")

# ==========================================
# 6. INFERÊNCIA (CORRIGIDA)
# ==========================================
print("\n🤖 === TESTE DE INFERÊNCIA (PÓS-TREINO) ===")

# A. Limpeza de Memória e Troca de Modo
model.eval() # <--- O PULO DO GATO 1: Desliga dropout e coloca em modo de avaliação

# B. Ajuste do Tokenizer para Geração
tokenizer.padding_side = "left" # <--- O PULO DO GATO 2: Para gerar, padding é à esquerda

# C. Definição do Prompt de Teste
test_messages = [
    {"role": "system", "content": "You are an insurance expert. Context: Claims"},
    {"role": "user", "content": "What is considered a total loss?"}
]
input_text = tokenizer.apply_chat_template(test_messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(input_text, return_tensors="pt").to(device)

# D. Geração com Parâmetros de Controle (Evita o Loop Infinito)
with torch.no_grad(): # Economiza memória
    outputs = model.generate(
        **inputs, 
        max_new_tokens=200, 
        temperature=0.3, 
        do_sample=True,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id, # <--- O PULO DO GATO 3: Define fim explicitamente
        eos_token_id=tokenizer.eos_token_id
    )

# E. Decodificação Limpa
response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

print("-" * 50)
print(f"PERGUNTA: What is considered a total loss?")
print("-" * 50)
print(f"RESPOSTA:\n{response.strip()}")
print("-" * 50)