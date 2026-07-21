import base64
import numpy as np
import os
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer

# Load Sentence Transformers model optimized for semantic text search
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load CSV - use path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "faq_seed.csv")
data = pd.read_csv(csv_path)

# Loop through each FAQ
for _, row in data.iterrows():
    question = row["question"]
    answer = row["answer"]

    # Generate text embedding using Sentence Transformers
    # Automatically normalized and optimized for semantic similarity
    embedding = model.encode(question, normalize_embeddings=True)

    # Convert embedding to Base64
    embedding_bytes = embedding.astype(np.float32).tobytes()
    embedding_b64 = base64.b64encode(embedding_bytes).decode("utf-8")

    # Send to API
    response = requests.post(
        "http://localhost:8000/faq",
        json={
            "question": question,
            "answer": answer,
            "embedding": embedding_b64,
        },
    )

    if response.status_code == 200:
        print(f"FAQ added successfully: {response.status_code}")
    else:
        print(f"FAQ failed: {response.status_code} - {response.text}")