from brain.llm import LLM


class RAGQA:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = LLM()

    def answer(self, query: str):
        # 🔍 Retrieve context
        chunks = self.retriever.retrieve(query)

        context = "\n".join(chunks)

        # 🧠 Build prompt
        prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}

Answer concisely.
"""

        return self.llm.generate(prompt)