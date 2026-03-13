from sentence_transformers import SentenceTransformer
import re
from config import EMBEDDING_MODEL_NAME


# -------------------------------------------------------
# LOAD MODEL (ONLY ONCE)
# -------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------------------------------------
# TEXT CLEANING FOR EMBEDDING
# -------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text before generating embeddings.
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# -------------------------------------------------------
# GENERATE EMBEDDING
# -------------------------------------------------------

def generate_embedding(text: str):
    """
    Convert message into embedding vector.
    """
    text = normalize_text(text)
    embedding = model.encode(text)

    return embedding.tolist()