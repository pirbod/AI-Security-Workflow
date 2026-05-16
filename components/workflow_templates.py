from __future__ import annotations

import json

import streamlit as st

from utils.state import load_workflow_templates


def _template_by_id(template_id: str) -> dict:
    return next(template for template in load_workflow_templates() if template["id"] == template_id)


def _render_template_card(template: dict) -> None:
    st.markdown(
        f"""
        <div class="template-card">
            <div style="font-weight: 750; font-size: 1.05rem;">{template["name"]}</div>
            <p class="small-muted">{template["description"]}</p>
            <span class="badge badge-neutral">{template["trigger"]}</span>
            <div style="margin-top: .75rem;"><b>Impact:</b> {template["automation_impact"]}</div>
            <div class="small-muted" style="margin-top: .4rem;">{", ".join(template["nodes_used"][:4])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Open Template", key=f"open-{template['id']}", use_container_width=True):
        st.session_state.open_template_id = template["id"]


def render() -> None:
    st.markdown('<div class="app-title">Workflow Templates</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Reusable n8n-oriented playbooks for security operations teams.</div>',
        unsafe_allow_html=True,
    )

    templates = load_workflow_templates()
    for start in range(0, len(templates), 3):
        columns = st.columns(3)
        for column, template in zip(columns, templates[start : start + 3]):
            with column:
                _render_template_card(template)

    st.divider()
    selected = _template_by_id(st.session_state.open_template_id)
    st.subheader(selected["name"])
    overview, payload = st.columns([1.15, 1])
    with overview:
        st.markdown("**Description**")
        st.write(selected["description"])
        st.markdown("**Business value**")
        st.write(selected["business_value"])
        st.markdown("**Security value**")
        st.write(selected["security_value"])
        st.markdown("**Workflow steps**")
        for index, step in enumerate(selected["workflow_steps"], start=1):
            st.write(f"{index}. {step}")
    with payload:
        st.markdown("**Mock payload**")
        st.code(json.dumps(selected["mock_payload"], indent=2), language="json")
        st.markdown("**Expected output**")
        st.code(json.dumps(selected["expected_output"], indent=2), language="json")
        st.markdown("**Recommended production integrations**")
        st.write(", ".join(selected["production_integrations"]))
