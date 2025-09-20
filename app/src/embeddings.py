# src/embeddings.py
import os
import numpy as np

USE_OPENAI = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"

if USE_OPENAI:
    import openai
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_KEY

    def get_embedding(text):
        resp = openai.Embedding.create(model="text-embedding-3-small", input=text)
        return np.array(resp["data"][0]["embedding"])
else:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    def get_embedding(text):
        return model.encode(text, show_progress_bar=False)
