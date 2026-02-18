

import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

# =========================================================
# SAFE IMPORT
# =========================================================
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except Exception:
    PINECONE_AVAILABLE = False
    logger.warning("⚠ Pinecone not installed → memory disabled")


# =========================================================
# MAIN CLASS
# =========================================================
class PineconeStore:
    def __init__(self):

        self.enabled = False
        self.index = None

        # -----------------------------
        # If library missing → disable
        # -----------------------------
        if not PINECONE_AVAILABLE:
            logger.info("📦 Pinecone disabled (library missing)")
            return

        api_key = os.getenv("PINECONE_API_KEY")

        # -----------------------------
        # If no API key → disable
        # -----------------------------
        if not api_key:
            logger.info("📦 Pinecone disabled (no API key)")
            return

        try:
            pc = Pinecone(api_key=api_key)
            index_name = "clauseai-memory"

            # -----------------------------
            # Check existing indexes
            # -----------------------------
            try:
                existing = [i["name"] for i in pc.list_indexes()]
            except Exception:
                existing = pc.list_indexes().names()

            # -----------------------------
            # Create index if not exists
            # -----------------------------
            if index_name not in existing:
                logger.info("Creating Pinecone index...")
                pc.create_index(
                    name=index_name,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )

            self.index = pc.Index(index_name)
            self.enabled = True
            logger.info("✅ Pinecone memory enabled")

        except Exception as e:
            logger.error(f"Pinecone init failed: {e}")
            self.enabled = False

    # =========================================================
    # STORE CONTRACT MEMORY
    # =========================================================
    def store_contract(self, contract_id: str, text: str, contract_type: str = ""):

        if not self.enabled:
            logger.debug("Memory disabled → skip store")
            return False

        try:
            vector = self._fake_embedding(text)

            metadata = {
                "contract_type": contract_type or "Unknown",
                "preview": text[:200]
            }

            self.index.upsert(
                vectors=[{
                    "id": contract_id,
                    "values": vector,
                    "metadata": metadata
                }]
            )

            logger.info("📦 Contract stored in memory")
            return True

        except Exception as e:
            logger.error(f"Memory store error: {e}")
            return False

    # =========================================================
    # SEARCH SIMILAR CONTRACTS
    # =========================================================
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

            results = []
            matches = res.get("matches", []) if isinstance(res, dict) else res.matches

            for m in matches:
                meta = m.get("metadata", {}) if isinstance(m, dict) else m.metadata
                score = m.get("score", 0) if isinstance(m, dict) else m.score
                idx = m.get("id", "") if isinstance(m, dict) else m.id

                results.append({
                    "id": idx,
                    "score": round(score, 3),
                    "metadata": meta or {}
                })

            return results

        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []

    # =========================================================
    # LIGHTWEIGHT EMBEDDING (NO OPENAI NEEDED)
    # =========================================================
    def _fake_embedding(self, text: str):
        """
        Simple hash embedding
        No OpenAI required
        """
        import hashlib

        h = hashlib.md5(text.encode()).hexdigest()
        vec = [int(h[i:i+2], 16) / 255 for i in range(0, 32, 2)]
        return vec + [0.0] * (384 - len(vec))


# =========================================================
# SINGLETON ACCESS
# =========================================================
_pinecone_instance = None

def get_memory():
    global _pinecone_instance
    if _pinecone_instance is None:
        _pinecone_instance = PineconeStore()
    return _pinecone_instance
