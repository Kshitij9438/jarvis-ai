import os
from rag.loaders.pdf_loader import load_pdf
from rag.loaders.text_loader import load_txt
from rag.loaders.md_loader import load_md
from rag.loader import chunk_text


class Ingestor:
    def __init__(self, embedder, store):
        self.embedder = embedder
        self.store = store

    def load_file(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = load_pdf(file_path)

        elif ext == ".txt":
            text = load_txt(file_path)

        elif ext == ".md":
            text = load_md(file_path)

        else:
            return f"❌ Unsupported file type: {ext}"

        if not text.strip():
            return "⚠️ No readable content found."

        chunks = chunk_text(text)
        embeddings = self.embedder.embed(chunks)

        self.store.add(chunks, embeddings)

        return f"✅ Loaded {file_path} with {len(chunks)} chunks"