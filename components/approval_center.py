from __future__ import annotations

import streamlit as st

from utils.state import get_incident, update_approval, update_incident


STATUS_BADGE = {
    "Pending": "badge-medium",
    "Approved": "badge-low",
    "Rejected": "badge-critical",
    "More context requested": "badge-neutral",
}


def _set_decision(approval_id: str, incident_id: str, status: str) -> None:
    update_approval(approval_id, status)
    if status == "Approved":
        update_incident(incident_id, status="Approved action", ticket_status="Created")
    elif status == "Rejected":
        update_incident(incident_id, status="Action rejected")
    else:
        update_incident(incident_id, status="More context requested")
    st.rerun()


def render() -> None:
    st.markdown('<div class="app-title">Human Approval Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Governance layer for high-impact security actions before tickets, notifications, or remediation proceed.</div>',
        unsafe_allow_html=True,
    )

    pending = sum(1 for item in st.session_state.approvals if item["status"] == "Pending")
    st.metric("Pending approval actions", pending)

    for item in st.session_state.approvals:
        incident = get_incident(item["incident_id"])
        with st.container(border=True):
            header = st.columns([0.64, 0.18, 0.18])
            with header[0]:
                st.markdown(f"**{item['action']}**")
                st.caption(f"{incident['id']} · {incident['title']} · {incident['source']}")
            with header[1]:
                st.markdown(f'<span class="badge badge-neutral">{item["risk"]}</span>', unsafe_allow_html=True)
            with header[2]:
                badge = STATUS_BADGE.get(item["status"], "badge-neutral")
                st.markdown(f'<span class="badge {badge}">{item["status"]}</span>', unsafe_allow_html=True)

            detail_cols = st.columns(2)
            with detail_cols[0]:
                st.markdown("**Reason approval is required**")
                st.write(item["reason"])
            with detail_cols[1]:
                st.markdown("**Impact**")
                st.write(item["impact"])

            actions = st.columns(3)
            with actions[0]:
                st.button(
                    "Approve",
                    key=f"approve-{item['id']}",
                    disabled=item["status"] == "Approved",
                    use_container_width=True,
                    on_click=_set_decision,
                    args=(item["id"], item["incident_id"], "Approved"),
                )
            with actions[1]:
                st.button(
                    "Reject",
                    key=f"reject-{item['id']}",
                    disabled=item["status"] == "Rejected",
                    use_container_width=True,
                    on_click=_set_decision,
                    args=(item["id"], item["incident_id"], "Rejected"),
                )
            with actions[2]:
                st.button(
                    "Request more context",
                    key=f"context-{item['id']}",
                    disabled=item["status"] == "More context requested",
                    use_container_width=True,
                    on_click=_set_decision,
                    args=(item["id"], item["incident_id"], "More context requested"),
                )
