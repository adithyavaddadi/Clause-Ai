import streamlit as st
from utils.history_manager import check_duplicate, get_contract



# =========================================================
# HANDLE DUPLICATE CONTRACT
# =========================================================
def handle_duplicate(contract_text):
    """
    Checks if contract already analyzed.
    Returns:
        ("load", data)  -> load old result
        ("reanalyze", None) -> run new analysis
        ("new", None) -> brand new contract
    """

    exists, hash_id = check_duplicate(contract_text)

    if not exists:
        return "new", None

    data = get_contract(hash_id)

    st.warning("⚠ This contract was already analyzed earlier.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📂 Load Previous Analysis"):
            return "load", data

    with col2:
        if st.button("🔁 Re-Analyze Contract"):
            return "reanalyze", None

    st.stop()
