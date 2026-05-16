from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


LAYERS = {
    "Input Sources": ["Checkmk", "Wazuh", "Suricata", "Kubernetes", "Cloud audit logs", "GitHub", "Gozar probes", "CVE feeds"],
    "n8n Orchestration Layer": [
        "Webhook intake",
        "Workflow routing",
        "Enrichment",
        "AI agent call",
        "Risk scoring",
        "Human approval",
        "Ticketing",
        "Notification",
        "Evidence packaging",
    ],
    "AI Triage Layer": [
        "Local LLM compatible interface",
        "Incident memory",
        "Vector search placeholder",
        "Deterministic PoC scoring",
        "Future RAG capability",
    ],
    "Approval and Governance": ["Manual approvals", "Action records", "Policy gates", "Decision history"],
    "Output Systems": ["Jira", "ServiceNow", "Slack", "Microsoft Teams", "GitHub Issues", "SIEM"],
    "Evidence and Audit Layer": ["Markdown evidence package", "JSON evidence package", "Timeline", "Risk explanation"],
}


def _architecture_sankey() -> go.Figure:
    labels = list(LAYERS.keys())
    source = [0, 1, 1, 2, 3, 4]
    target = [1, 2, 3, 3, 4, 5]
    value = [8, 5, 4, 3, 6, 4]
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(label=labels, pad=22, thickness=18, color=["#2563eb", "#0f766e", "#7c3aed", "#f97316", "#0891b2", "#16a34a"]),
                link=dict(source=source, target=target, value=value, color="rgba(148, 163, 184, 0.28)"),
            )
        ]
    )
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    return fig


def render() -> None:
    st.markdown('<div class="app-title">Architecture</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Target operating model: detections stay in source tools, n8n coordinates enrichment, governance, output, and evidence.</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(_architecture_sankey(), use_container_width=True)

    for start in range(0, len(LAYERS), 3):
        columns = st.columns(3)
        for column, (title, items) in zip(columns, list(LAYERS.items())[start : start + 3]):
            with column:
                st.markdown(
                    f"""
                    <div class="info-card">
                        <div style="font-weight: 760; font-size: 1.05rem; margin-bottom: .55rem;">{title}</div>
                        <div class="small-muted">{" · ".join(items)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()
    st.subheader("Operating Principle")
    st.write(
        "n8n is the automation and orchestration layer. Detection sources create alerts, workflows enrich and route them, "
        "the AI triage layer summarizes context, human approval governs risky actions, and evidence packages preserve the record."
    )
