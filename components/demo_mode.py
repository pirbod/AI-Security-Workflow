from __future__ import annotations

import streamlit as st

from components.workflow_canvas import WORKFLOW_NODES
from utils.exporters import write_json_package, write_markdown_package
from utils.mock_ai import generate_ai_triage
from utils.scoring import calculate_risk
from utils.state import get_incident, set_selected_incident, update_approval, update_incident


DEMO_INCIDENT_ID = "INC-1005"
DEMO_STAGES = [
    "Select Kubernetes privileged pod incident",
    "Receive alert through webhook-style intake",
    "Normalize and enrich event context",
    "Generate deterministic AI triage result",
    "Calculate risk score",
    "Route high-risk action to approval queue",
    "Approve demo action",
    "Generate evidence package",
    "Update dashboard metrics",
]


def _run_demo() -> None:
    set_selected_incident(DEMO_INCIDENT_ID)
    incident = get_incident(DEMO_INCIDENT_ID)
    score = calculate_risk(incident)
    generate_ai_triage(incident)
    st.session_state.workflow_completed_nodes = [node["name"] for node in WORKFLOW_NODES]
    st.session_state.demo_runs += 1
    st.session_state.demo_last_stage = "Completed"

    for item in st.session_state.approvals:
        if item["incident_id"] == DEMO_INCIDENT_ID and item["action"] == "Disable service account":
            update_approval(item["id"], "Approved")
            break

    markdown_path = write_markdown_package(incident, "Approved remediation", "Generated for demo review")
    json_path = write_json_package(incident, "Approved remediation", "Generated for demo review")
    st.session_state.generated_packages[f"{incident['id']}-markdown"] = str(markdown_path)
    st.session_state.generated_packages[f"{incident['id']}-json"] = str(json_path)
    update_incident(
        DEMO_INCIDENT_ID,
        status="Evidence generated",
        approval_required=score.approval_required,
        ticket_status="Created",
        evidence_package_status="Generated",
    )


def render() -> None:
    st.markdown('<div class="app-title">Demo Mode</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">One-click stakeholder flow showing alert intake, enrichment, AI triage, approval, and evidence generation.</div>',
        unsafe_allow_html=True,
    )

    action_col, status_col = st.columns([0.35, 0.65])
    with action_col:
        if st.button("Run Demo Incident", type="primary", use_container_width=True):
            _run_demo()
            st.rerun()
    with status_col:
        st.metric("Demo runs", st.session_state.demo_runs)
        st.caption(f"Last stage: {st.session_state.demo_last_stage}")

    completed = st.session_state.demo_last_stage == "Completed"
    progress = 1.0 if completed else 0.0
    st.progress(progress)

    for index, stage in enumerate(DEMO_STAGES, start=1):
        done = completed
        badge = "Completed" if done else "Ready"
        css = "badge-low" if done else "badge-neutral"
        st.markdown(
            f"""
            <div class="stage-card" style="margin-bottom: .55rem;">
                <span class="badge {css}">{badge}</span>
                <b>{index}. {stage}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if completed:
        incident = get_incident(DEMO_INCIDENT_ID)
        ai = generate_ai_triage(incident)
        st.divider()
        st.subheader("Demo Result")
        st.write(ai["reasoning_summary"])
        st.write(f"Risk score: **{incident['risk_score']}** · Ticket status: **{incident['ticket_status']}** · Evidence: **{incident['evidence_package_status']}**")
