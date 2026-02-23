# =========================================================
# CLAUSE AI - PROFESSIONAL INTERNSHIP VERSION (FINAL)
# Premium Dark Startup UI + Clean Planner Output
# =========================================================

from __future__ import annotations
import streamlit as st
import os, tempfile, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import docx

load_dotenv()

# ===== IMPORT AGENTS =====
from agents_llm.classifier_agent import classify_contract
from agents_llm.legal_agent import legal_agent
from agents_llm.finance_agent import finance_agent
from agents_llm.compliance_agent import compliance_agent
from agents.review_planner import create_review_plan
from report.final_report import generate_final_report
from report.final_report_utils import extract_risk_metrics
from utils.hybrid_llm import call_hybrid_llm

APP_TITLE = "ClauseAI — Contract Intelligence"
MAX_TEXT = 15000

# =========================================================
# 🎨 PREMIUM DARK STARTUP UI
# =========================================================
def inject_style():
    st.markdown("""
    <style>
    .stApp{
        background: linear-gradient(180deg,#020617,#020617,#020617);
        color:#e5e7eb;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
    }

    .title{
        font-size:2.7rem;
        font-weight:700;
        background: linear-gradient(90deg,#60a5fa,#a78bfa,#22d3ee);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        margin-bottom:25px;
    }

    .card{
        padding:22px;
        border-radius:18px;
        margin-bottom:18px;
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(16px);
        border:1px solid rgba(255,255,255,0.08);
        box-shadow:0 8px 30px rgba(0,0,0,0.45);
        transition: all .25s ease;
    }

    .card:hover{
        transform: translateY(-3px);
        box-shadow:0 12px 40px rgba(0,0,0,0.55);
    }

    .legal{border-left:4px solid #fb7185;}
    .finance{border-left:4px solid #facc15;}
    .compliance{border-left:4px solid #34d399;}
    .final{
        border-left:4px solid #a78bfa;
        box-shadow:0 0 25px rgba(167,139,250,0.15);
    }
    .dash{border-left:4px solid #60a5fa;}

    .highlight{
        background:rgba(255,255,255,0.04);
        padding:14px;
        border-radius:12px;
        margin-top:10px;
        line-height:1.6;
        color:#cbd5e1;
    }

    .planner{
        background:rgba(255,255,255,0.05);
        padding:16px;
        border-radius:14px;
        margin-bottom:12px;
        border-left:4px solid #60a5fa;
        box-shadow:0 4px 18px rgba(0,0,0,0.35);
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
def build_dynamic_prompt(text, tone, agent_name):
    return f"""
You are {agent_name} contract analysis AI.
Tone: {tone}
Analyze contract and give structured insights.

Contract:
{text}
"""

def build_dashboard_summary(legal, finance, compliance):
    return f"""
### ⚖ Legal
{legal[:250]}

### 💰 Financial
{finance[:250]}

### 🛡 Compliance
{compliance[:250]}
"""

# =========================================================
def init_session():
    defaults = {
        "done": False,
        "contract_type": "",
        "agents": {},
        "report": "",
        "planner": {},
        "summary":""
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# =========================================================
def load_file(uploaded):
    suffix = uploaded.name.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix="."+suffix) as tmp:
        tmp.write(uploaded.read())
        path = tmp.name

    try:
        if suffix == "pdf":
            return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
        if suffix == "docx":
            return "\n".join(p.text for p in docx.Document(path).paragraphs)
        return open(path,encoding="utf-8",errors="ignore").read()
    finally:
        os.remove(path)

def fetch_url(url):
    r = requests.get(url, timeout=20)
    if "html" in r.headers.get("content-type",""):
        return BeautifulSoup(r.text,"html.parser").get_text("\n")
    return r.text

# =========================================================
def run_agents(text, ctype, focus, tone):

    agents = {
        "Legal": legal_agent,
        "Finance": finance_agent,
        "Compliance": compliance_agent,
    }

    results = {}

    def run(name, fn):
        try:
            prompt = build_dynamic_prompt(text, tone, name)
            try:
                return name, fn(prompt, ctype, focus)
            except:
                return name, fn(prompt)
        except Exception as e:
            return name, f"Error: {e}"

    with ThreadPoolExecutor(max_workers=3) as ex:
        futures=[ex.submit(run,n,f) for n,f in agents.items()]
        for f in as_completed(futures):
            k,v=f.result()
            results[k]=v

    return results

# =========================================================
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_pdf(text):
    styles = getSampleStyleSheet()
    elements = []
    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 8))

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()
    doc = SimpleDocTemplate(tmp.name)
    doc.build(elements)

    with open(tmp.name, "rb") as f:
        data = f.read()

    os.unlink(tmp.name)
    return data

# =========================================================
def main():
    st.set_page_config(page_title="ClauseAI", layout="wide")
    inject_style()
    init_session()

    st.markdown(f"<div class='title'>{APP_TITLE}</div>", unsafe_allow_html=True)

    focus = st.text_input("Focus area (optional)")
    tone = st.selectbox("Report tone",
        ["Professional","Strict Legal","Executive","Friendly","Risk Auditor","Investor"]
    )

    input_type = st.radio("Input method", ["Upload","Paste","URL"], horizontal=True)

    uploaded=None
    pasted=""
    url=""

    if input_type=="Upload":
        uploaded = st.file_uploader("Upload contract", type=["pdf","docx","txt"])
    elif input_type=="Paste":
        pasted = st.text_area("Paste contract text")
    else:
        url = st.text_input("Enter URL")

    if st.button("Analyze Contract", use_container_width=True):

        text=None
        if uploaded: text=load_file(uploaded)
        elif pasted: text=pasted
        elif url: text=fetch_url(url)

        if not text or len(text)<50:
            st.error("Contract too short")
            return

        text=text[:MAX_TEXT]

        with st.spinner("Analyzing contract..."):
            ctype = classify_contract(text)
            agent_outputs = run_agents(text, ctype, focus, tone)

            final_report = generate_final_report(
                contract_type=ctype,
                legal=agent_outputs.get("Legal",""),
                finance=agent_outputs.get("Finance",""),
                compliance=agent_outputs.get("Compliance",""),
                user_focus=f"{focus} | Tone:{tone}"
            )

            planner = create_review_plan(text, ctype, focus)

        st.session_state.done=True
        st.session_state.contract_type=ctype
        st.session_state.agents=agent_outputs
        st.session_state.report=final_report
        st.session_state.planner=planner
        st.session_state.summary = build_dashboard_summary(
            agent_outputs.get("Legal",""),
            agent_outputs.get("Finance",""),
            agent_outputs.get("Compliance","")
        )

        st.success("Analysis complete")

    # =========================================================
    if st.session_state.done:

        tab1,tab2,tab3,tab4,tab5 = st.tabs([
            "📊 Executive Dashboard",
            "🤖 AI Risk Analysis",
            "💬 AI Assistant",
            "📑 Final Contract Report",
            "🧭 Review & Action Plan"
        ])

        # DASHBOARD
        with tab1:
            risk,percent = extract_risk_metrics(st.session_state.report)

            c1,c2,c3 = st.columns(3)
            c1.metric("Contract Type", st.session_state.contract_type)
            c2.metric("Risk Level", risk)
            c3.metric("Risk Score", f"{percent}%")

            st.markdown(
                f"<div class='card dash'><h3>Executive Summary</h3><div class='highlight'>{st.session_state.summary}</div></div>",
                unsafe_allow_html=True
            )

            pdf = export_pdf(st.session_state.report)
            st.download_button("Download Final Report", pdf, "ClauseAI_Report.pdf")

        # AGENTS
        with tab2:
            for k,v in st.session_state.agents.items():
                cls="legal" if k=="Legal" else "finance" if k=="Finance" else "compliance"
                icon="⚖️" if k=="Legal" else "💰" if k=="Finance" else "🛡"

                st.markdown(
                    f"<div class='card {cls}'><h3>{icon} {k}</h3><div class='highlight'>{v}</div></div>",
                    unsafe_allow_html=True
                )

        # CHAT
        with tab3:
            q = st.text_area("Ask question about contract")
            if st.button("Ask"):
                ans = call_hybrid_llm(
                    f"Contract:\n{st.session_state.report}\nQuestion:{q}",
                    role="chat"
                )
                st.markdown(f"<div class='card dash'>{ans}</div>", unsafe_allow_html=True)

        # FINAL REPORT
        with tab4:
            st.markdown(
                f"<div class='card final'><h2>Final Contract Report</h2>{st.session_state.report}</div>",
                unsafe_allow_html=True
            )

               # =========================================================
        # 🧭 REVIEW PLANNER
        # =========================================================
        with tab5:
            plan = st.session_state.planner

            st.markdown(
                "<div class='card final'><h3>🧭 Smart Contract Review Planner</h3></div>",
                unsafe_allow_html=True
            )

            # Handle multiple possible return formats
            if isinstance(plan, dict):
                checklist = (
                    plan.get("review_checklist")
                    or plan.get("checklist")
                    or plan.get("tasks")
                    or []
                )
            elif isinstance(plan, list):
                checklist = plan
            else:
                checklist = []

            if not checklist:
                st.warning("Planner returned empty structure.")
                st.write("DEBUG OUTPUT:", plan)
            else:
                for idx, item in enumerate(checklist, start=1):

                    if isinstance(item, dict):
                        area = (
                            item.get("area")
                            or item.get("title")
                            or item.get("section")
                            or f"Section {idx}"
                        )

                        check = (
                            item.get("check")
                            or item.get("description")
                            or item.get("action")
                            or item.get("task")
                            or str(item)
                        )
                    else:
                        area = f"Section {idx}"
                        check = str(item)

                    st.markdown(f"""
                    <div class='planner'>
                        <b>{idx}. 📌 {area}</b><br>
                        <span style='color:#cbd5e1'>✔ {check}</span>
                    </div>
                    """, unsafe_allow_html=True)
if __name__ == "__main__":
    main()