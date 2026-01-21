import joblib
import numpy as np
from skl2onnx import to_onnx
from skl2onnx.common.data_types import FloatTensorType

# Carregar o modelo
model = joblib.load("random_forest_model.joblib")

# DEFINIÇÃO CRUCIAL:
# Nomeamos a entrada como 'float_input'
# O shape [None, 4] diz: "Aceite qualquer número de linhas (None), mas exatamente 4 colunas (features)"
initial_type = [('float_input', FloatTensorType([None, 4]))]

# 3. Converter DESATIVANDO o ZipMap
# O 'options' abaixo é o segredo para o Triton aceitar o modelo
options = {id(model): {'zipmap': False}}

# Converter
onx = to_onnx(model, initial_types=initial_type, target_opset=15, options=options)

with open("random_forest.onnx", "wb") as f:
    f.write(onx.SerializeToString())

print("Modelo ONNX exportado com suporte a Batching!")