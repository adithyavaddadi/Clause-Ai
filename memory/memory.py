"""
Contract Memory System
Stores contract sessions + analysis history
Stable + reusable + duplicate detection
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import hashlib
import uuid

logger = logging.getLogger(__name__)


class ContractMemory:
    """
    Local memory for storing contract sessions & analysis history
    """

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.contract_hash_map: Dict[str, str] = {}

    # --------------------------------------------------
    # CREATE NEW SESSION
    # --------------------------------------------------
    def create_session(self, contract_name: str, contract_text: str, contract_type: str) -> str:

        if not contract_text:
            raise ValueError("Empty contract text")

        # ---- duplicate check ----
        duplicate = self.find_duplicate(contract_text)
        if duplicate:
            logger.info(f"Duplicate contract detected → using existing session {duplicate}")
            return duplicate

        # ---- unique session id ----
        session_id = f"contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"

        self.sessions[session_id] = {
            "name": contract_name or "Untitled Contract",
            "text": contract_text,
            "type": contract_type or "Unknown",
            "analyses": {},
            "final_report": "",
            "created": datetime.now().strftime("%d %b %Y %H:%M"),
        }

        # ---- store hash for duplicate detection ----
        h = self._hash(contract_text)
        self.contract_hash_map[h] = session_id

        logger.info(f"Created new contract session: {session_id}")
        return session_id

    # --------------------------------------------------
    # STORE AGENT RESULT
    # --------------------------------------------------
    def store_analysis(self, session_id: str, agent_name: str, result: str):

        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        session["analyses"][agent_name] = result or ""

    # --------------------------------------------------
    # STORE FINAL REPORT
    # --------------------------------------------------
    def store_final_report(self, session_id: str, report: str):

        session = self.sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return

        session["final_report"] = report or ""

    # --------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------
    def find_duplicate(self, contract_text: str) -> Optional[str]:
        if not contract_text:
            return None

        h = self._hash(contract_text)
        return self.contract_hash_map.get(h)

    # --------------------------------------------------
    # GET SESSION
    # --------------------------------------------------
    def get_session(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)

    # --------------------------------------------------
    # LIST HISTORY
    # --------------------------------------------------
    def list_history(self) -> List[Dict]:

        history = []
        for sid, data in self.sessions.items():
            history.append({
                "session_id": sid,
                "name": data.get("name", ""),
                "type": data.get("type", ""),
                "created": data.get("created", "")
            })

        # newest first
        history.sort(key=lambda x: x["created"], reverse=True)
        return history

    # --------------------------------------------------
    # INTERNAL HASH
    # --------------------------------------------------
    def _hash(self, text: str) -> str:
        return hashlib.md5(text.strip().encode()).hexdigest()


# --------------------------------------------------
# SINGLETON MEMORY INSTANCE
# --------------------------------------------------
_memory_instance: Optional[ContractMemory] = None


def get_memory() -> ContractMemory:
    global _memory_instance

    if _memory_instance is None:
        _memory_instance = ContractMemory()

    return _memory_instance
