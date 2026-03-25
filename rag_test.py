from rag.embedder import Embedder
from rag.store import VectorStore
from rag.loader import chunk_text
from rag.retriever import Retriever

text = """
Soft computing is a collection of methodologies that aim to exploit tolerance 
for imprecision and uncertainty to achieve tractability, robustness, and low cost.
"""

chunks = chunk_text(text)

embedder = Embedder()
embeddings = embedder.embed(chunks)

store = VectorStore()
store.add(chunks, embeddings)

retriever = Retriever(embedder, store)

results = retriever.retrieve("What is soft computing?")

for r in results:
    print("RESULT:", r)