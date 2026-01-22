from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List
from fastbm25 import fastbm25

class RetrievalPlatform:
    def __init__(self):
        # Usando memória para garantir que rode aí sem precisar configurar Docker agora
        # Se quiser usar Docker, mude para "http://localhost:6333"
        self.client = QdrantClient(":memory:") 
        self.dense_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            
    def create_collection(self, name):
        if self.client.collection_exists(collection_name=name):
            self.client.delete_collection(collection_name=name)
        
        self.client.create_collection(
            collection_name=name,
            # Vetor denso padrão (sem nome)
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            # Vetor esparso nomeado
            sparse_vectors_config={
                "text-sparse": models.SparseVectorParams()
            }
        )

    def _get_sparse_vector(self, text: str):
        tokens = text.lower().split()
        if not tokens:
            return models.SparseVector(indices=[], values=[])
            
        model = fastbm25([tokens])
        
        indices = []
        values = []
        
        for word in set(tokens):
            # Usamos o IDF para o peso
            weight = model.idf.get(word, 0.0)
            if weight > 0:
                idx = abs(hash(word)) % 1000000
                indices.append(idx)
                values.append(float(weight))
            
        return models.SparseVector(indices=indices, values=values)

    def ingest(self, collection: str, documents: List[str]):
        points = []
        for i, doc in enumerate(documents):
            dense_vec = self.dense_model.encode(doc).tolist()
            sparse_vec = self._get_sparse_vector(doc)
            
            points.append(
                models.PointStruct(
                    id=i,
                    vector={
                        "": dense_vec,          # Vetor padrão (sem nome)
                        "text-sparse": sparse_vec # Vetor nomeado
                    },
                    payload={"text": doc}
                )
            )
        
        self.client.upsert(collection_name=collection, points=points)
        print(f"Ingestão de {len(documents)} documentos concluída.")

    def hybrid_search(self, query, collection):
        query_dense = self.dense_model.encode(query).tolist()
        query_sparse = self._get_sparse_vector(query)
        
        # --- CORREÇÃO DEFINITIVA ---
        # A nova API usa 'query' e 'using', não 'vector'.
        results = self.client.query_points(
            collection_name=collection,
            prefetch=[
                models.Prefetch(
                    query=query_dense,  # O dado vai aqui (lista de floats)
                    using=None,         # None = usa o vetor padrão (denso)
                    limit=20
                ),
                models.Prefetch(
                    query=query_sparse, # O dado vai aqui (SparseVector)
                    using="text-sparse",# Nome do vetor esparso configurado
                    limit=20
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=10
        ).points
        
        if not results:
            return []

        passages = [res.payload['text'] for res in results]
        ranks = self.reranker.predict([(query, p) for p in passages])
        
        combined = sorted(zip(results, ranks), key=lambda x: x[1], reverse=True)
        return combined[:5]

# --- Execução ---
if __name__ == "__main__":
    documents = [
        "A política de reembolso da nossa startup permite devoluções em até 30 dias.",
        "O servidor de produção deve ser reiniciado apenas aos domingos às 03:00.",
        "O CTO definiu que usaremos vLLM para escalar nossos modelos."
    ]

    platform = RetrievalPlatform()
    
    print("Criando coleção...")
    platform.create_collection("startup_docs")
    platform.ingest("startup_docs", documents)

    print("\n--- Buscando por 'reembolso' ---")
    results = platform.hybrid_search("reembolso", "startup_docs")
    for point, rank_score in results:
        print(f"Score: {rank_score:.4f} | {point.payload['text']}")