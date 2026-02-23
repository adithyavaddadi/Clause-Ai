import streamlit as st

# =========================================================
# SHORT CLEAN LINE EXTRACTOR
# =========================================================
def _short(text: str):
    if not text:
        return "No major issues detected"

    lines = text.split("\n")
    for l in lines:
        l = l.strip()
        if len(l) > 15:
            return l[:100]

    return text[:100]


# =========================================================
# MINI SNAPSHOT (DASHBOARD)
# =========================================================
def show_reasoning_snapshot(legal, finance, compliance, risk):

    st.markdown("### 🧠 AI Risk Reasoning Snapshot")

    st.markdown(f"""
    <div style='
    padding:18px;
    border-radius:16px;
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    line-height:1.9;
    font-size:16px;
    backdrop-filter: blur(12px);
    '>

    ⚖ <b>Legal:</b> {_short(legal)}<br>
    💰 <b>Finance:</b> {_short(finance)}<br>
    🛡 <b>Compliance:</b> {_short(compliance)}<br>
    📊 <b>Overall Risk Score:</b> <b>{risk}</b>

    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FULL AI DECISION FLOW (PRO VERSION)
# =========================================================
def show_ai_decision_flow(legal, finance, compliance, risk):

    st.markdown("## 🧠 AI Decision Intelligence Flow")

    # color glow based on risk
    glow = "#22c55e"
    if "HIGH" in risk.upper():
        glow = "#fb7185"
    elif "MEDIUM" in risk.upper():
        glow = "#facc15"

    steps = [
        "📄 Contract uploaded & parsed",
        f"⚖ Legal Intelligence → {_short(legal)}",
        f"💰 Financial Intelligence → {_short(finance)}",
        f"🛡 Compliance Intelligence → {_short(compliance)}",
        f"📊 Risk Engine → Overall Risk: <b>{risk}</b>",
        "✅ AI Recommendation generated"
    ]

    st.markdown(f"""
    <style>
    .flow-card {{
        padding:18px;
        margin:14px 0;
        border-radius:16px;
        background:rgba(255,255,255,0.06);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 0 25px {glow}40;
        font-size:17px;
        backdrop-filter: blur(12px);
        animation: fadeInUp .6s ease forwards;
    }}

    .arrow {{
        text-align:center;
        font-size:22px;
        opacity:.6;
        margin-bottom:6px;
    }}

    @keyframes fadeInUp {{
        from {{opacity:0; transform:translateY(20px);}}
        to {{opacity:1; transform:translateY(0);}}
    }}
    </style>
    """, unsafe_allow_html=True)

    # render flow
    for step in steps:
        st.markdown(f"<div class='flow-card'>{step}</div>", unsafe_allow_html=True)
        st.markdown("<div class='arrow'>⬇</div>", unsafe_allow_html=True)

    st.markdown("---")

    # replay button (clean rerun)
    if st.button("🔁 Replay AI Flow Animation"):
        st.rerun()
