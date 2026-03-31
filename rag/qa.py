from brain.llm import LLM


class RAGQA:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = LLM()

    def answer(self, query: str):
        chunks = self.retriever.retrieve(query)

        # 🔥 FALLBACK TO GENERAL KNOWLEDGE
        if not chunks:
            return self.llm.generate_text(
                f"Answer this from general knowledge:\n{query}"
            )

        context = "\n".join(chunks)

        prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}

Answer concisely and only using the provided context.
"""

        return self.llm.generate_text(prompt)