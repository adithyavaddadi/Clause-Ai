import os
import json
import hashlib
from datetime import datetime

HISTORY_FILE = "data/contracts_history.json"
MAX_HISTORY = 10


# =====================================================
# ensure folder exists
# =====================================================
def _ensure():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump({}, f)


# =====================================================
# LOAD HISTORY
# =====================================================
def load_history():
    _ensure()
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


# =====================================================
# SAVE HISTORY
# =====================================================
def _save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =====================================================
# CREATE HASH FOR CONTRACT
# =====================================================
def get_contract_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# =====================================================
# ADD CONTRACT TO HISTORY
# =====================================================
def save_contract(
    contract_name,
    contract_text,
    contract_type,
    risk_level,
    final_report,
    agents,
    planner
):
    history = load_history()
    h = get_contract_hash(contract_text)

    history[h] = {
        "name": contract_name,
        "date": datetime.now().strftime("%d %b %Y %H:%M"),
        "risk": risk_level,
        "contract_type": contract_type,
        "report": final_report,
        "agents": agents,
        "planner": planner,
        "text": contract_text
    }

    # keep only last 10
    if len(history) > MAX_HISTORY:
        oldest = list(history.keys())[0]
        del history[oldest]

    _save_history(history)


# =====================================================
# CHECK DUPLICATE
# =====================================================
def check_duplicate(contract_text):
    history = load_history()
    h = get_contract_hash(contract_text)
    return h in history, h


# =====================================================
# GET CONTRACT BY HASH
# =====================================================
def get_contract(hash_id):
    history = load_history()
    return history.get(hash_id)


# =====================================================
# GET ALL HISTORY LIST
# =====================================================
def get_all_history():
    history = load_history()
    items = []

    for h, data in history.items():
        items.append({
            "hash": h,
            "name": data.get("name"),
            "date": data.get("date"),
            "risk": data.get("risk")
        })

    # newest first
    items.reverse()
    return items
