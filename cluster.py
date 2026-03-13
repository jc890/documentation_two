import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import SIMILARITY_THRESHOLD
from sklearn.feature_extraction.text import TfidfVectorizer

# -------------------------------------------------------
# COSINE SIMILARITY
# -------------------------------------------------------

def similarity_score(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """

    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)

    score = cosine_similarity(vec1, vec2)[0][0]

    return float(score)


# -------------------------------------------------------
# FIND CLUSTER
# -------------------------------------------------------

def assign_cluster(new_embedding, existing_faults):
    """
    Assign cluster ID based on similarity.

    existing_faults = list of tuples
    (cluster_id, embedding)
    """

    best_cluster = None
    best_score = 0

    for cluster_id, emb in existing_faults:

        score = similarity_score(new_embedding, emb)

        if score > best_score:
            best_score = score
            best_cluster = cluster_id

    if best_score >= SIMILARITY_THRESHOLD:
        return best_cluster

    return None
