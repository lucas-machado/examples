import os
import xgboost as xgb
import numpy as np
from sklearn.datasets import make_classification

# 1. Parâmetros de infraestrutura do modelo
MODEL_NAME = "credit_score_model"
MODEL_VERSION = "1"
EXPORT_PATH = f"./model_repository/{MODEL_NAME}/{MODEL_VERSION}"

# Criar a estrutura de pastas se não existir
os.makedirs(EXPORT_PATH, exist_ok=True)

# 2. Gerar dados sintéticos (Simulando 10.000 perfis de clientes)
# 10 features: Renda, Idade, Score Serasa, Tempo de Emprego, etc.
X, y = make_classification(
    n_samples=10000, 
    n_features=10, 
    n_informative=8, 
    random_state=42
)

# 3. Treinar o XGBoost
print(f"🚀 Treinando o modelo {MODEL_NAME}...")
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective="binary:logistic",
    tree_method="hist" # Otimizado para CPU/GPU
)

model.fit(X, y)

# 4. Exportar para o formato JSON (Recomendado para o Triton FIL backend)
# O backend FIL da NVIDIA lê JSON ou o formato binário do XGBoost.
model_file = os.path.join(EXPORT_PATH, "model.json")
model.save_model(model_file)

print(f"✅ Modelo exportado com sucesso em: {model_file}")
print(f"💡 Lembre-se: o 'config.pbtxt' que criamos deve estar na pasta: ./model_repository/{MODEL_NAME}/")