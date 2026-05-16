from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.state import get_incident, set_selected_incident, update_incident


FILTERS = [
    "All",
    "Critical",
    "High",
    "Needs approval",
    "Auto-resolved",
    "False positive",
    "Evidence generated",
]


def _matches_filter(incident: dict, filter_name: str) -> bool:
    if filter_name == "All":
        return True
    if filter_name in {"Critical", "High"}:
        return incident["severity"] == filter_name
    if filter_name == "Needs approval":
        return incident["approval_required"] or incident["status"] in {"Needs approval", "Queued for approval"}
    return incident["status"] == filter_name or incident.get("evidence_package_status") == filter_name.replace("-", " ").title()


def _severity_badge(severity: str) -> str:
    css = severity.lower()
    return f'<span class="badge badge-{css}">{severity}</span>'


def render() -> None:
    st.markdown('<div class="app-title">Incident Triage</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Mock incidents from security tooling, enriched for explainable AI triage and workflow routing.</div>',
        unsafe_allow_html=True,
    )

    selected_filter = st.radio("Filter", FILTERS, horizontal=True, label_visibility="collapsed")
    filtered = [incident for incident in st.session_state.incidents if _matches_filter(incident, selected_filter)]

    list_col, detail_col = st.columns([1.1, 1])
    with list_col:
        st.subheader(f"{len(filtered)} incidents")
        for incident in filtered:
            with st.container(border=True):
                top = st.columns([0.72, 0.28])
                with top[0]:
                    st.markdown(f"**{incident['id']}** · {incident['title']}")
                    st.markdown(
                        f"{_severity_badge(incident['severity'])}<span class=\"badge badge-neutral\">{incident['source']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"{incident['asset']} · {incident['environment']} · Risk {incident['risk_score']}")
                with top[1]:
                    if st.button("View", key=f"view-{incident['id']}", use_container_width=True):
                        set_selected_incident(incident["id"])

    with detail_col:
        incident = get_incident()
        st.subheader(f"{incident['id']} · {incident['title']}")
        st.markdown(
            f"{_severity_badge(incident['severity'])}<span class=\"badge badge-neutral\">Risk {incident['risk_score']}</span><span class=\"badge badge-neutral\">Confidence {incident['confidence_score']}</span>",
            unsafe_allow_html=True,
        )
        st.write(incident["raw_alert"])

        fields = pd.DataFrame(
            [
                ("Source", incident["source"]),
                ("Asset", incident["asset"]),
                ("Environment", incident["environment"]),
                ("MITRE-style tactic", incident["mitre_tactic"]),
                ("Recommended action", incident["recommended_action"]),
                ("Status", incident["status"]),
                ("Approval required", "Yes" if incident["approval_required"] else "No"),
                ("Ticket status", incident["ticket_status"]),
                ("Evidence package status", incident["evidence_package_status"]),
            ],
            columns=["Field", "Value"],
        )
        st.dataframe(fields, hide_index=True, use_container_width=True)

        st.markdown("**Enriched context**")
        st.json(incident["enriched_context"], expanded=False)

        actions = st.columns(3)
        with actions[0]:
            if st.button("Mark triaged", use_container_width=True):
                update_incident(incident["id"], status="In triage")
                st.rerun()
        with actions[1]:
            if st.button("Mark false positive", use_container_width=True):
                update_incident(incident["id"], status="False positive", ticket_status="Closed")
                st.rerun()
        with actions[2]:
            if st.button("Mark evidence ready", use_container_width=True):
                update_incident(incident["id"], evidence_package_status="Generated")
                st.rerun()
