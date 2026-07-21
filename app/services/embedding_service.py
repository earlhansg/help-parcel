import base64
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with Sentence Transformers model optimized for semantic text search.
        all-MiniLM-L6-v2: 384 dimensions, fast, good quality for FAQ matching.
        """
        self.model = SentenceTransformer(model_name)
    
    def text_to_embedding(self, text: str) -> str:
        """
        Convert text to base64-encoded embedding using Sentence Transformers.
        Optimized for semantic text similarity (384 dimensions).
        """
        # Generate embedding vector (normalized by default)
        embedding_vector = self.model.encode(text, normalize_embeddings=True)
        
        # Convert to bytes and then base64 encode
        embedding_bytes = embedding_vector.astype(np.float32).tobytes()
        embedding_base64 = base64.b64encode(embedding_bytes).decode('utf-8')
        
        return embedding_base64
    
    def texts_to_embeddings(self, texts: List[str]) -> List[str]:
        """
        Convert multiple texts to embeddings (batch processing for efficiency).
        Much faster than individual conversions for multiple texts.
        """
        # Generate embeddings for all texts at once (batch processing)
        embedding_vectors = self.model.encode(texts, normalize_embeddings=True)
        embeddings = []
        
        for vector in embedding_vectors:
            embedding_bytes = vector.astype(np.float32).tobytes()
            embedding_base64 = base64.b64encode(embedding_bytes).decode('utf-8')
            embeddings.append(embedding_base64)
            
        return embeddings