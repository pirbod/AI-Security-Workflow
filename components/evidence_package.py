from __future__ import annotations

import json

import streamlit as st

from utils.exporters import build_evidence_package, render_markdown, write_json_package, write_markdown_package
from utils.state import get_incident, incident_options, set_selected_incident, update_incident


def render() -> None:
    st.markdown('<div class="app-title">Evidence Package</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Generate local markdown and JSON records that preserve alert context, triage reasoning, decisions, and mitigations.</div>',
        unsafe_allow_html=True,
    )

    options = incident_options()
    labels = list(options.keys())
    current = get_incident()
    current_label = next(label for label, value in options.items() if value == current["id"])
    selected_label = st.selectbox("Incident", labels, index=labels.index(current_label))
    set_selected_incident(options[selected_label])
    incident = get_incident()

    decision = st.selectbox("Analyst decision", ["Pending review", "Approved remediation", "Rejected remediation", "False positive", "Evidence only"])
    final_status = st.selectbox("Final status", ["Generated for demo review", "Open", "Closed", "Escalated", "Resolved"])

    summary = st.columns(4)
    summary[0].metric("Incident", incident["id"])
    summary[1].metric("Severity", incident["severity"])
    summary[2].metric("Risk", incident["risk_score"])
    summary[3].metric("Confidence", incident["confidence_score"])

    actions = st.columns(4)
    with actions[0]:
        if st.button("Generate Markdown", use_container_width=True):
            path = write_markdown_package(incident, decision, final_status)
            st.session_state.generated_packages[f"{incident['id']}-markdown"] = str(path)
            update_incident(incident["id"], evidence_package_status="Generated")
            st.success(f"Generated {path}")
    with actions[1]:
        if st.button("Generate JSON", use_container_width=True):
            path = write_json_package(incident, decision, final_status)
            st.session_state.generated_packages[f"{incident['id']}-json"] = str(path)
            update_incident(incident["id"], evidence_package_status="Generated")
            st.success(f"Generated {path}")
    with actions[2]:
        preview = st.button("Preview Report", use_container_width=True)
    with actions[3]:
        st.button("Generate PDF", disabled=True, use_container_width=True)

    st.divider()
    tabs = st.tabs(["Preview", "JSON", "Generated files"])
    with tabs[0]:
        if preview or True:
            st.markdown(render_markdown(incident, decision, final_status))
    with tabs[1]:
        st.code(json.dumps(build_evidence_package(incident, decision, final_status), indent=2), language="json")
    with tabs[2]:
        if st.session_state.generated_packages:
            for artifact, path in sorted(st.session_state.generated_packages.items()):
                st.write(f"- {artifact}: `{path}`")
        else:
            st.caption("No local package files generated yet.")
