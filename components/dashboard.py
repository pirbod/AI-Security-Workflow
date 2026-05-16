from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.state import dashboard_metrics


def _metric_card(label: str, value: object) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _status_for_incident(row: pd.Series) -> str:
    if row["status"] in {"Auto-resolved", "False positive", "Evidence generated"}:
        return "Completed"
    if row["approval_required"]:
        return "Waiting approval"
    return "In progress"


def render() -> None:
    st.markdown('<div class="app-title">AI Security Workflow Orchestrator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Executive view of n8n-orchestrated AI-native security workflows across mock detection sources.</div>',
        unsafe_allow_html=True,
    )

    metrics = dashboard_metrics()
    first_row = st.columns(4)
    second_row = st.columns(4)
    for column, (label, value) in zip(first_row + second_row, metrics.items()):
        with column:
            _metric_card(label, value)

    incidents = pd.DataFrame(st.session_state.incidents)
    incidents["workflow_status"] = incidents.apply(_status_for_incident, axis=1)

    st.divider()
    chart_a, chart_b = st.columns(2)
    with chart_a:
        source_counts = incidents.groupby("source", as_index=False).size().rename(columns={"size": "Incidents"})
        fig = px.bar(source_counts, x="source", y="Incidents", color="source", title="Incidents by source")
        fig.update_layout(showlegend=False, height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with chart_b:
        severity_order = ["Critical", "High", "Medium", "Low"]
        severity_counts = incidents.groupby("severity", as_index=False).size().rename(columns={"size": "Incidents"})
        fig = px.bar(
            severity_counts,
            x="severity",
            y="Incidents",
            color="severity",
            category_orders={"severity": severity_order},
            title="Incidents by severity",
        )
        fig.update_layout(showlegend=False, height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    chart_c, chart_d = st.columns(2)
    with chart_c:
        status_counts = incidents.groupby("workflow_status", as_index=False).size().rename(columns={"size": "Executions"})
        fig = px.pie(status_counts, names="workflow_status", values="Executions", hole=0.58, title="Workflow execution status")
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with chart_d:
        fig = px.histogram(incidents, x="confidence_score", nbins=8, title="Confidence score distribution")
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20), yaxis_title="Incidents")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Executions")
    recent = incidents.assign(
        **{
            "Execution ID": [f"WF-{1000 + index}" for index in range(len(incidents))],
            "Source": incidents["source"],
            "Workflow": incidents["event_type"].str.replace("_", " ").str.title(),
            "Severity": incidents["severity"],
            "Risk score": incidents["risk_score"],
            "Status": incidents["workflow_status"],
            "Last updated": incidents["timestamp"],
        }
    )
    st.dataframe(
        recent[["Execution ID", "Source", "Workflow", "Severity", "Risk score", "Status", "Last updated"]],
        use_container_width=True,
        hide_index=True,
    )
