import logging
import hashlib
import numpy as np
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try importing google.generativeai
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Try importing sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingService:
    def __init__(self):
        self.embedding_dim = 384
        self.use_gemini = False
        self.local_model = None

        if settings.GEMINI_API_KEY and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.use_gemini = True
                logger.info("Configured Google Gemini Embeddings.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini embeddings: {e}")
                self.use_gemini = False

        if not self.use_gemini and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.local_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.embedding_dim = 384
                logger.info("Loaded local SentenceTransformer all-MiniLM-L6-v2.")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers: {e}")
                self.local_model = None

    def _fallback_deterministic_embed(self, text: str, dim: int = 384) -> List[float]:
        """Fast, deterministic fallback vector generator for testing when no neural model is available."""
        words = text.lower().split()
        vector = np.zeros(dim, dtype=np.float32)
        if not words:
            return vector.tolist()
        
        for w in words:
            # Hash word into fixed buckets
            hash_val = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = hash_val % dim
            sign = 1.0 if ((hash_val >> 4) % 2 == 0) else -1.0
            vector[idx] += sign * (1.0 + len(w) * 0.1)

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # 1. Try Gemini API
        if self.use_gemini and settings.GEMINI_API_KEY:
            try:
                embeddings = []
                for text in texts:
                    response = genai.embed_content(
                        model=settings.EMBEDDING_MODEL or "models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    embeddings.append(response['embedding'])
                return embeddings
            except Exception as e:
                logger.warning(f"Gemini embedding call failed, falling back: {e}")

        # 2. Try SentenceTransformers
        if self.local_model is not None:
            try:
                embeddings = self.local_model.encode(texts, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"Local sentence-transformers embedding failed: {e}")

        # 3. Deterministic semantic hash fallback
        return [self._fallback_deterministic_embed(t, self.embedding_dim) for t in texts]


embedding_service = EmbeddingService()
