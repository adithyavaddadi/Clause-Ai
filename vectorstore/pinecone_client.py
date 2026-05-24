"""
Pinecone Vector Memory Client Store
Allows storing and searching contract history semantically using lightweight MD5 hash embeddings.
Operates gracefully by disabling itself if credentials or packages are missing.
"""

from __future__ import annotations
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# =========================================================
# SAFE DEPENDENCY LOADING
# =========================================================
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except Exception:
    PINECONE_AVAILABLE = False
    logger.warning("⚠ Pinecone package not installed. Memory vector engine will be disabled.")


# =========================================================
# PINECONE STORE ENGINE
# =========================================================
class PineconeStore:
    """Manages active vector indexing and querying tasks for semantic contract retrieval."""

    def __init__(self) -> None:
        """Initializes client index, verifies remote keys, and provisions serverless store if needed."""
        self.enabled = False
        self.index = None

        if not PINECONE_AVAILABLE:
            logger.info("📦 Pinecone memory disabled (library is missing).")
            return

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            logger.info("📦 Pinecone memory disabled (API key is not configured).")
            return

        try:
            pc = Pinecone(api_key=api_key)
            index_name = "clauseai-memory"

            # Retrieve active cloud indexes
            try:
                existing = [i["name"] for i in pc.list_indexes()]
            except Exception:
                existing = pc.list_indexes().names()

            # Create index if it does not exist
            if index_name not in existing:
                logger.info(f"Creating Pinecone index: '{index_name}'...")
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
            logger.info("✅ Pinecone semantic memory store successfully enabled.")

        except Exception as e:
            logger.error(f"Pinecone client initialization failed: {e}")
            self.enabled = False

    # =========================================================
    # STORE CONTRACT DATA
    # =========================================================
    def store_contract(self, contract_id: str, text: str, contract_type: str = "") -> bool:
        """Saves a contract block and its metadata to the Pinecone index.
        
        Args:
            contract_id (str): Unique identifier for the contract.
            text (str): Raw contract context.
            contract_type (str): Classified category.
            
        Returns:
            bool: True on successful upsert, False otherwise.
        """
        if not self.enabled or self.index is None:
            logger.debug("Memory disabled → skipping Pinecone upsert operation.")
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

            logger.info(f"📦 Contract '{contract_id}' stored in Pinecone vector index.")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert contract to Pinecone: {e}")
            return False

    # =========================================================
    # SEMANTIC SIMILARITY SEARCH
    # =========================================================
    def search_similar(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries Pinecone for semantically similar contracts.
        
        Args:
            text (str): Search query or contract context.
            top_k (int): Number of top matches to return.
            
        Returns:
            List[Dict[str, Any]]: List of top matches with scores and metadata.
        """
        if not self.enabled or self.index is None:
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
                score = m.get("score", 0.0) if isinstance(m, dict) else m.score
                idx = m.get("id", "") if isinstance(m, dict) else m.id

                results.append({
                    "id": idx,
                    "score": round(score, 3),
                    "metadata": meta or {}
                })

            return results

        except Exception as e:
            logger.error(f"Pinecone query search failed: {e}")
            return []

    # =========================================================
    # LIGHTWEIGHT HASH EMBEDDING
    # =========================================================
    def _fake_embedding(self, text: str) -> List[float]:
        """Creates a fast, deterministic MD5-based hash embedding (384-d).
        
        Removes dependencies on external embedding provider services for quick demo runs.
        
        Args:
            text (str): Input text chunk.
            
        Returns:
            List[float]: 384-dimensional normalized float array.
        """
        import hashlib

        h = hashlib.md5(text.strip().encode()).hexdigest()
        vec = [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]
        
        # Pad vector to match the 384-dimension requirements of the Pinecone index
        return vec + [0.0] * (384 - len(vec))


# =========================================================
# SINGLETON ACCESS ADAPTER
# =========================================================
_pinecone_instance: PineconeStore | None = None


def get_memory() -> PineconeStore:
    """Returns a cached, globally accessible single instance of PineconeStore."""
    global _pinecone_instance
    if _pinecone_instance is None:
        _pinecone_instance = PineconeStore()
    return _pinecone_instance


def get_pinecone() -> PineconeStore:
    """Legacy helper for testing backward compatibility."""
    return get_memory()

