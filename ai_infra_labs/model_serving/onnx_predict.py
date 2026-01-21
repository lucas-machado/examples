import onnxruntime as rt
import numpy as np

sess = rt.InferenceSession("random_forest.onnx", providers=["CPUExecutionProvider"])

# Pegamos o nome exato da entrada definido na exportação
input_name = sess.get_inputs()[0].name # Será 'float_input'

# O dado precisa ser 2D: (1 linha, 4 colunas)
test_data = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)

# Execução
pred_onx = sess.run(None, {input_name: test_data})[0]

print(f"Input Name: {input_name}")
print(f"Predição: {pred_onx}")