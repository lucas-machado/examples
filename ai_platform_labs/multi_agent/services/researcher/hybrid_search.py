from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import List
from fastbm25 import fastbm25

class RetrievalPlatform:
    def __init__(self):
        # In-memory for lab simplicity
        self.client = QdrantClient(":memory:") 
        self.dense_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            
    def create_collection(self, name):
        if self.client.collection_exists(collection_name=name):
            self.client.delete_collection(collection_name=name)
        
        self.client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
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
                        "": dense_vec,
                        "text-sparse": sparse_vec
                    },
                    payload={"text": doc}
                )
            )
        
        self.client.upsert(collection_name=collection, points=points)
        print(f"Ingested {len(documents)} documents into '{collection}'.")

    def hybrid_search(self, query, collection):
        query_dense = self.dense_model.encode(query).tolist()
        query_sparse = self._get_sparse_vector(query)
        
        results = self.client.query_points(
            collection_name=collection,
            prefetch=[
                models.Prefetch(
                    query=query_dense,
                    using=None,
                    limit=20
                ),
                models.Prefetch(
                    query=query_sparse,
                    using="text-sparse",
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
