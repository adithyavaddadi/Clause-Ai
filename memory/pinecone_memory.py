"""
Pinecone Vector Memory Store (Optional AI Memory)
Used for similarity search between contracts
Safe + optional + production ready
"""

import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

# ---------------- TRY IMPORT PINECONE ----------------
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except Exception:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not installed → running without vector DB")


class PineconeStore:
    """
    Optional vector memory for contract similarity
    If pinecone not available → system still works
    """

    def __init__(self):
        self.enabled = False
        self.index = None

        if not PINECONE_AVAILABLE:
            return

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            logger.warning("No Pinecone API key → disabled")
            return

        try:
            pc = Pinecone(api_key=api_key)

            index_name = "clauseai-memory"

            # -------- check existing indexes ----------
            existing = []
            try:
                existing = [i["name"] for i in pc.list_indexes()]
            except:
                pass

            if index_name not in existing:
                logger.info("Creating Pinecone index...")
                pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )

            self.index = pc.Index(index_name)
            self.enabled = True
            logger.info("Pinecone initialized successfully")

        except Exception as e:
            logger.error(f"Pinecone init failed: {e}")
            self.enabled = False

    # --------------------------------------------------
    # STORE CONTRACT VECTOR
    # --------------------------------------------------
    def store_contract(self, contract_id: str, text: str, contract_type: str) -> bool:

        if not self.enabled:
            return False

        try:
            vector = self._fake_embedding(text)

            metadata = {
                "contract_type": contract_type,
                "preview": text[:200],
            }

            self.index.upsert(
                vectors=[{
                    "id": contract_id,
                    "values": vector,
                    "metadata": metadata
                }]
            )

            logger.info("Stored contract in Pinecone")
            return True

        except Exception as e:
            logger.error(f"Pinecone store error: {e}")
            return False

    # --------------------------------------------------
    # SEARCH SIMILAR CONTRACTS
    # --------------------------------------------------
    def search_similar(self, text: str, top_k: int = 3) -> List[Dict]:

        if not self.enabled:
            return []

        try:
            vector = self._fake_embedding(text)

            res = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )

            matches = res.get("matches", []) if isinstance(res, dict) else res.matches

            results = []
            for m in matches:
                results.append({
                    "id": m.id if hasattr(m, "id") else m.get("id"),
                    "score": round(m.score if hasattr(m, "score") else m.get("score", 0), 3),
                    "metadata": m.metadata if hasattr(m, "metadata") else m.get("metadata", {})
                })

            return results

        except Exception as e:
            logger.error(f"Pinecone search error: {e}")
            return []

    # --------------------------------------------------
    # FAKE EMBEDDING (FAST DEMO)
    # Replace with real embeddings later
    # --------------------------------------------------
    def _fake_embedding(self, text: str):

        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()

        vec = [int(h[i:i+2], 16)/255 for i in range(0, 32, 2)]
        return vec + [0.0] * (384 - len(vec))


# --------------------------------------------------
# SINGLETON
# --------------------------------------------------
_pinecone_instance = None


def get_pinecone() -> PineconeStore:
    global _pinecone_instance

    if _pinecone_instance is None:
        _pinecone_instance = PineconeStore()

    return _pinecone_instance
