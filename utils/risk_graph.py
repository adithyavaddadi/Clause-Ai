import plotly.graph_objects as go
import streamlit as st


def show_risk_radar(legal, finance, compliance):

    def score(txt):
        txt = txt.lower()
        if "high" in txt: return 80
        if "medium" in txt: return 55
        if "low" in txt: return 25
        return min(len(txt)//25, 90)

    legal_s = score(legal)
    fin_s = score(finance)
    comp_s = score(compliance)

    categories = ["Legal Risk", "Financial Risk", "Compliance Risk"]
    values = [legal_s, fin_s, comp_s]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        hovertemplate="<b>%{theta}</b><br>Risk Score: %{r}%<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0,100]
            )
        ),
        showlegend=False,
        height=420,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
