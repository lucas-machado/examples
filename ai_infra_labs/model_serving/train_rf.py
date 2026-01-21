import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. Carregar dados (4 features: comprimento/largura de sépala e pétala)
data = load_iris()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Configurar o Modelo
# n_estimators = número de árvores na floresta
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

# 3. Treinar (Fit)
print("Treinando o modelo...")
model.fit(X_train, y_train)

# 4. Avaliar
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Acurácia do modelo: {accuracy * 100:.2f}%")

# 5. Salvar o modelo (Serialização tradicional)
joblib.dump(model, "random_forest_model.joblib")
print("Modelo salvo como 'random_forest_model.joblib'")