from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[str], top_k: int = 3):
        """
        Rerank documents based on relevance to query
        """

        if not documents:
            return []

        # Pair query with each doc
        pairs = [(query, doc) for doc in documents]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Sort by score (descending)
        ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)

        # Extract top_k docs
        top_docs = [doc for _, doc in ranked[:top_k]]

        return top_docs