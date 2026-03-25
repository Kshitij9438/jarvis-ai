import numpy as np


class VectorStore:
    def __init__(self):
        self.vectors = []
        self.texts = []

    def add(self, texts, embeddings):
        for text, emb in zip(texts, embeddings):
            self.texts.append(text)
            self.vectors.append(emb)

    def search(self, query_embedding, top_k=3):
        if not self.vectors:
            return []

        vectors = np.array(self.vectors)

        similarities = np.dot(vectors, query_embedding) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_embedding)
        )

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [self.texts[i] for i in top_indices]