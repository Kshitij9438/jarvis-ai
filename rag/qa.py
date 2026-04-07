from brain.llm import LLM


class RAGQA:
    def __init__(self, retriever, ingestor):
        self.retriever = retriever
        self.ingestor = ingestor
        self.llm = LLM()

    # =========================
    # 📄 LOAD FILE
    # =========================
    def load_file(self, file_path: str):
        return self.ingestor.load_file(file_path)

    # =========================
    # 🧠 CHECK IF DOCUMENT EXISTS
    # =========================
    def has_documents(self):
        return len(self.retriever.store.vectors) > 0

    # =========================
    # 🤖 ANSWER QUERY
    # =========================
    def answer(self, query: str):
        # 🚨 SAFETY CHECK
        if not self.has_documents():
            return "⚠️ No document loaded. Please load a file first."

        chunks = self.retriever.retrieve(query)

        # 🚨 NO RETRIEVAL RESULT
        if not chunks:
            return "⚠️ No relevant information found in the document."

        context = "\n".join(chunks)

        prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}

Answer concisely and ONLY using the provided context.
"""

        return self.llm.generate_text(prompt)