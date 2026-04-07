from sentence_transformers import SentenceTransformer
import numpy as np


class SemanticMatcher:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # cache tool embeddings
        self.tool_embeddings = {}

    # =========================
    # 🧠 EMBED TEXT
    # =========================
    def embed(self, text: str):
        return self.model.encode([text])[0]

    # =========================
    # 🧠 PRECOMPUTE TOOL EMBEDDINGS
    # =========================
    def register_tool(self, tool):
        corpus = []

        # combine intents + description
        if hasattr(tool, "intents"):
            corpus.extend(tool.intents)

        if hasattr(tool, "description"):
            corpus.append(tool.description)

        if not corpus:
            corpus = [tool.name]

        embeddings = self.model.encode(corpus)
        self.tool_embeddings[tool.name] = embeddings

    # =========================
    # 🧠 SIMILARITY
    # =========================
    def similarity(self, query: str, tool):
        query_emb = self.embed(query)

        tool_embs = self.tool_embeddings.get(tool.name, [])

        if len(tool_embs) == 0:
            return 0.0

        sims = np.dot(tool_embs, query_emb) / (
            np.linalg.norm(tool_embs, axis=1) * np.linalg.norm(query_emb)
        )

        return float(np.max(sims))