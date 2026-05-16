from __future__ import annotations

import json

import streamlit as st

from utils.state import get_ai_for_selected, get_incident, incident_options, set_selected_incident


def render() -> None:
    st.markdown('<div class="app-title">AI Agent Panel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Deterministic mock triage output showing how an AI layer can summarize enriched workflow context.</div>',
        unsafe_allow_html=True,
    )

    options = incident_options()
    current = get_incident()
    labels = list(options.keys())
    current_label = next(label for label, value in options.items() if value == current["id"])
    selected_label = st.selectbox("Selected incident", labels, index=labels.index(current_label))
    set_selected_incident(options[selected_label])

    incident = get_incident()
    ai = get_ai_for_selected()

    top = st.columns([1, 1, 1])
    top[0].metric("Risk score", incident["risk_score"])
    top[1].metric("Confidence score", ai["confidence_score"])
    top[2].metric("MITRE-style category", ai["mitre_category"])

    st.divider()
    raw_col, normalized_col = st.columns(2)
    with raw_col:
        st.subheader("Raw Alert")
        st.write(incident["raw_alert"])
        st.subheader("Enrichment Summary")
        st.write(ai["enrichment_summary"])
    with normalized_col:
        st.subheader("Normalized Event")
        st.code(json.dumps(ai["normalized_event"], indent=2), language="json")

    reasoning, remediation = st.columns(2)
    with reasoning:
        st.subheader("AI Reasoning Summary")
        st.info(ai["reasoning_summary"])
        st.subheader("Risk Explanation")
        st.write(ai["risk_explanation"])
    with remediation:
        st.subheader("Recommended Remediation")
        st.success(ai["recommended_remediation"])
        st.subheader("Evidence References")
        for reference in ai["evidence_references"]:
            st.write(f"- {reference}")
