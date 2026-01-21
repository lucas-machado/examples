import numpy as np
import tritonclient.http as httpclient

# 1. Conexão com o servidor
URL = "localhost:8000"
MODEL_NAME = "random_forest"

client = httpclient.InferenceServerClient(url=URL)

# 2. Preparação dos dados de entrada
# Simulando 3 flores de uma vez para testar o Batching que configuramos
data = np.array([
    [5.1, 3.5, 1.4, 0.2],  # Iris Setosa
    [6.7, 3.0, 5.2, 2.3],  # Iris Virginica
    [5.9, 3.0, 4.2, 1.5]   # Iris Versicolor
], dtype=np.float32)

# 3. Criar os objetos de Input do Triton
# O shape deve ser [Número de Exemplos, 4]
inputs = [
    httpclient.InferInput("float_input", data.shape, "FP32")
]
inputs[0].set_data_from_numpy(data)

# 4. Definir o que queremos de volta
outputs = [
    httpclient.InferRequestedOutput("label"),
    httpclient.InferRequestedOutput("probabilities")
]

# 5. Executar a Inferência
print(f"Enviando lote de {data.shape[0]} amostras para o Triton...")
response = client.infer(model_name=MODEL_NAME, inputs=inputs, outputs=outputs)

# 6. Processar Resultados
labels = response.as_numpy("label")
probs = response.as_numpy("probabilities")

print("\n--- Resultados ---")
for i in range(len(labels)):
    print(f"Flor {i+1}: Classe Predita = {labels[i]}, Confiança = {np.max(probs[i]):.4f}")