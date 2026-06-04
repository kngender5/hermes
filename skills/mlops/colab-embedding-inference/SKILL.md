---
name: colab-embedding-inference
description: Serve embedding/reranker models (sentence-transformers, BGE, GTE, Jina, ColBERT) via Google Colab GPU + Gradio. For RAG, semantic search, similarity.
---

# Colab Embedding Inference — RAG & Semantic Search

Serve text/image embedding and reranker models on Google Colab GPU with Gradio UI.

## Supported Models

| Model | Dim | Task | VRAM | T4 OK |
|-------|-----|------|------|-------|
| all-MiniLM-L6-v2 | 384 | Embedding | ~90MB | ✅ |
| all-mpnet-base-v2 | 768 | Embedding | ~420MB | ✅ |
| BGE-large-en-v1.5 | 1024 | Embedding | ~1.3GB | ✅ |
| BGE-M3 | 1024 | Multi-lingual embed | ~1.3GB | ✅ |
| GTE-large | 1024 | Embedding | ~1.3GB | ✅ |
| Jina-embeddings-v3 | 1024 | Multi-lingual embed | ~1.5GB | ✅ |
| Jina-embeddings-v2-base-code | 768 | Code embed | ~500MB | ✅ |
| E5-mistral-7b-instruct | 4096 | Embedding | ~14GB | ✅ |
| BGE-reranker-v2-m3 | — | Reranker | ~1.3GB | ✅ |
| Jina-reranker-v2 | — | Reranker | ~1.5GB | ✅ |
| ColBERT | 128 | Late interaction | ~500MB | ✅ |
| CLIP ViT-L/14 | 768 | Image+Text embed | ~1GB | ✅ |

## requirements.txt
```
torch>=2.4.0
sentence-transformers>=3.4.0
gradio>=5.0.0
numpy>=2.0.0
scipy>=1.14.0
```

## Text Embeddings

### Basic embedding API
```python
!pip install sentence-transformers gradio -q

from sentence_transformers import SentenceTransformer
import gradio as gr
import numpy as np

model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")

def embed_texts(texts):
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

def similarity(text1, text2):
    emb1 = model.encode([text1], normalize_embeddings=True)
    emb2 = model.encode([text2], normalize_embeddings=True)
    sim = np.dot(emb1, emb2.T)[0][0]
    return f"Similarity: {sim:.4f}"

with gr.Blocks(title="BGE Embeddings") as demo:
    gr.Markdown("# 🔢 Text Embeddings")
    with gr.Tab("Similarity"):
        t1 = gr.Textbox(label="Text 1")
        t2 = gr.Textbox(label="Text 2")
        sim_out = gr.Textbox(label="Cosine Similarity")
        gr.Button("Compare").click(similarity, [t1, t2], sim_out)
    with gr.Tab("Embed"):
        txt = gr.Textbox(label="Text", lines=3)
        emb_out = gr.JSON(label="Embedding Vector")
        gr.Button("Embed").click(embed_texts, [txt], emb_out)

demo.launch(share=True, debug=True)
```

### Multi-lingual (BGE-M3 — supports 100+ languages)
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3", device="cuda")

# Supports: English, Norwegian, Chinese, Japanese, Korean, Arabic, etc.
embeddings = model.encode(
    ["Hello world", "Hei verden", "你好世界", "こんにちは世界"],
    normalize_embeddings=True,
)
```

### Code Embeddings (Jina v2)
```python
model = SentenceTransformer("jinaai/jina-embeddings-v2-base-code", device="cuda")
embeddings = model.encode(["def hello(): return 'world'"], normalize_embeddings=True)
```

## Reranker

```python
from sentence_transformers import CrossEncoder
import gradio as gr

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cuda")

def rerank(query, documents):
    if isinstance(documents, str):
        documents = documents.split("\n")
    pairs = [(query, doc) for doc in documents if doc.strip()]
    scores = reranker.predict(pairs)
    results = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return "\n".join([f"[{s:.4f}] {d}" for d, s in results])

with gr.Blocks(title="Reranker") as demo:
    gr.Markdown("# 🔄 BGE Reranker")
    query = gr.Textbox(label="Query")
    docs = gr.Textbox(label="Documents (one per line)", lines=10)
    out = gr.Textbox(label="Ranked Results", lines=10)
    gr.Button("Rerank").click(rerank, [query, docs], out)

demo.launch(share=True)
```

## Full RAG Pipeline (Embedding + Vector Search + LLM)

### requirements.txt
```
sentence-transformers>=3.4.0
faiss-gpu>=1.7.2  # or faiss-cpu
gradio>=5.0.0
transformers>=4.48.0
torch>=2.4.0
```

### Notebook Cell
```python
!pip install sentence-transformers faiss-gpu gradio transformers torch -q

import faiss, numpy as np, gradio as gr
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Embedder
embedder = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")

# LLM for answer generation
llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
               device_map="auto", torch_dtype=torch.float16)

# Sample documents
documents = [
    "The capital of Norway is Oslo.",
    "Tromsø is known as the Paris of the North.",
    "Sentence transformers convert text to vectors.",
    "FAISS is a library for efficient similarity search.",
    "RAG combines retrieval with language model generation.",
]

# Build index
doc_embeddings = embedder.encode(documents, normalize_embeddings=True)
index = faiss.IndexFlatIP(doc_embeddings.shape[1])
index.add(doc_embeddings.astype(np.float32))

def rag_query(query, top_k=3):
    # Retrieve
    q_emb = embedder.encode([query], normalize_embeddings=True).astype(np.float32)
    scores, indices = index.search(q_emb, top_k)
    retrieved = [documents[i] for i in indices[0]]
    
    # Generate
    context = "\n".join(retrieved)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    answer = llm(prompt, max_new_tokens=200, do_sample=False)[0]["generated_text"]
    answer = answer.split("Answer:")[-1].strip()
    
    sources = "\n".join([f"[{scores[0][i]:.3f}] {retrieved[i]}" for i in range(len(retrieved))])
    return answer, sources

with gr.Blocks(title="RAG Demo") as demo:
    gr.Markdown("# 🔍 RAG — Retrieval Augmented Generation")
    query = gr.Textbox(label="Question")
    answer = gr.Textbox(label="Answer", lines=5)
    sources = gr.Textbox(label="Retrieved Sources", lines=5)
    gr.Button("Ask").click(rag_query, [query], [answer, sources])

demo.launch(share=True, debug=True)
```

## Image Embeddings (CLIP)

```python
from sentence_transformers import SentenceTransformer
import gradio as gr

model = SentenceTransformer("clip-ViT-L-14", device="cuda")

def image_search(image, text):
    img_emb = model.encode([image])
    txt_emb = model.encode([text])
    sim = float(img_emb @ txt_emb.T)
    return f"Image-Text Similarity: {sim:.4f}"

with gr.Blocks() as demo:
    img = gr.Image(label="Image")
    txt = gr.Textbox(label="Text query")
    out = gr.Textbox(label="Similarity")
    gr.Button("Compare").click(image_search, [img, txt], out)

demo.launch(share=True)
```

## Common Issues

| Problem | Fix |
|---------|-----|
| FAISS GPU OOM | Use `faiss-cpu` instead, or reduce index size |
| Slow encoding | Batch encode: `model.encode(list_of_texts)` |
| Low similarity scores | Use `normalize_embeddings=True` |
| Model too large for T4 | Use `all-MiniLM-L6-v2` (384-dim, 90MB) |
| RAG poor quality | Increase top_k, use better embedder (BGE-large) |
| CUDA OOM with reranker | Process in batches of 32-64 pairs |
