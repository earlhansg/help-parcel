import base64
import numpy as np
import os
import pandas as pd
import requests
import torch

from transformers import CLIPProcessor, CLIPModel

# Load the processor and model
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

# Load CSV - use path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "faq_seed.csv")
data = pd.read_csv(csv_path)

# Loop through each FAQ
for _, row in data.iterrows():
    question = row["question"]
    answer = row["answer"]

    # Tokenize only the question
    inputs = processor(
        text=[question],
        return_tensors="pt",
        padding=True,
        truncation=True,
    )

    # Generate text embedding
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    # Normalize embedding
    embedding = text_features[0].numpy()
    embedding /= np.linalg.norm(embedding)

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