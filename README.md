# 🧠 Jarvis AI — A Fun Multi-Intent Agent 🤖

> A playful AI assistant that can open websites, read your documents, and answer questions using its own mini “brain”.

---

## 🚀 What is this?

Jarvis AI is a **fun experimental AI agent** I built to explore:

- 🧠 How LLMs can *plan actions*
- ⚙️ How tools can be *executed automatically*
- 📚 How AI can *read and understand your own files*

Think of it as a **mini Jarvis from Iron Man**—but built from scratch 😄

---

## ✨ What it can do

- 🌐 Open multiple websites from one sentence  
- 📄 Load your documents (PDF, TXT, MD)  
- 📚 Answer questions from your files (RAG)  
- 🧠 Understand multi-intent commands  
- 🔁 Combine multiple actions in one go  

---

## 🧪 Example

### Input:
```

open youtube and spotify and load C:\Users\HP\file.pdf

```

### Output:
```

✔ Opened YouTube
✔ Opened Spotify
✔ Loaded document (12 chunks)

```

---

## ⚙️ How it works (simple view)

```

You → AI Brain → Plan → Tools → Result

```

### More detailed:

```

User Input
↓
LLM (understands intent)
↓
Planner (creates steps)
↓
Executor (runs tools)
↓
Tools (web / RAG / files)
↓
Result

```

---

## 🧩 Features

- 🧠 Multi-intent understanding  
- 🛠️ Tool-based architecture  
- 📚 RAG (Retrieval-Augmented Generation)  
- 📄 Document ingestion system  
- ⚡ Fast local inference using Ollama  

---

## 📂 Project Structure

```

brain/        → LLM + prompts
planner/      → converts input → actions
executor/     → runs actions safely
tools/        → available tools (web, RAG, etc.)
rag/          → document search system
tests/        → unit tests

````

---

## 🛠️ Tech Stack

- Python 3.12  
- Ollama (for local LLMs)  
- sentence-transformers  
- Pytest  

---

## 🚀 How to run

```bash
uv run python main.py
````

Then try:

```
open youtube  
load C:\path\to\file.pdf  
summarize the document  
```

---

## 🧠 Why I built this

I wanted to move beyond:

```
“just calling an LLM”
```

and actually build something that:

* thinks in steps
* uses tools
* interacts with real data

---

## 🔮 Future Ideas

* 🧠 Smarter reasoning (reflection loop)
* 💾 Memory (remember past tasks)
* 🛡️ More reliable planning
* 📊 Better UI

---

## ⚠️ Note

This is a **learning + experimental project**, not production-ready.

Sometimes it might:

* misunderstand inputs
* give weird plans
* need retries

…and that’s part of the fun 😄

---

## 👤 Author

**Kshitij Shekhar**
That’s what makes it look 🔥 elite on GitHub.
```
