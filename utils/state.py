"""Streamlit state helpers for the local demo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from utils.mock_ai import generate_ai_triage
from utils.scoring import enrich_incidents_with_scores


DATA_DIR = Path("data")


def load_json(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_mock_incidents() -> list[dict[str, Any]]:
    return enrich_incidents_with_scores(load_json("mock_incidents.json"))


@st.cache_data(show_spinner=False)
def load_workflow_templates() -> list[dict[str, Any]]:
    return load_json("workflow_templates.json")


@st.cache_data(show_spinner=False)
def load_assets() -> list[dict[str, Any]]:
    return load_json("mock_assets.json")


@st.cache_data(show_spinner=False)
def load_cves() -> list[dict[str, Any]]:
    return load_json("mock_cve_context.json")


def initial_approval_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "APR-001",
            "action": "Restart Kubernetes pod",
            "incident_id": "INC-1004",
            "risk": "Medium",
            "reason": "Production workload restart can briefly affect payment processing.",
            "impact": "Short service interruption if replicas are unhealthy.",
            "status": "Pending",
        },
        {
            "id": "APR-002",
            "action": "Block suspicious IP",
            "incident_id": "INC-1003",
            "risk": "High",
            "reason": "Blocking network traffic may affect a legitimate partner integration.",
            "impact": "Potential egress disruption for workload-node-17.",
            "status": "Pending",
        },
        {
            "id": "APR-003",
            "action": "Disable service account",
            "incident_id": "INC-1005",
            "risk": "Critical",
            "reason": "The service account can create privileged workloads in production.",
            "impact": "May pause automation until ownership is confirmed.",
            "status": "Pending",
        },
        {
            "id": "APR-004",
            "action": "Create high-priority incident ticket",
            "incident_id": "INC-1001",
            "risk": "Critical",
            "reason": "Executive-facing checkout service is degraded.",
            "impact": "Creates visible P1 incident workflow.",
            "status": "Pending",
        },
        {
            "id": "APR-005",
            "action": "Escalate to incident commander",
            "incident_id": "INC-1007",
            "risk": "Critical",
            "reason": "Administrative role assignment changed in production cloud IAM.",
            "impact": "Starts formal incident command process.",
            "status": "Pending",
        },
        {
            "id": "APR-006",
            "action": "Trigger forensic evidence collection",
            "incident_id": "INC-1003",
            "risk": "High",
            "reason": "Potential command-and-control traffic requires preserved network evidence.",
            "impact": "Collects packet metadata and workflow records.",
            "status": "Pending",
        },
        {
            "id": "APR-007",
            "action": "Open GitHub security issue",
            "incident_id": "INC-1006",
            "risk": "High",
            "reason": "Finding should be tracked without exposing sensitive values.",
            "impact": "Notifies repository owner and starts remediation workflow.",
            "status": "Pending",
        },
    ]


def initialize_state() -> None:
    if "incidents" not in st.session_state:
        st.session_state.incidents = load_mock_incidents()
    if "selected_incident_id" not in st.session_state:
        st.session_state.selected_incident_id = "INC-1005"
    if "selected_workflow_node" not in st.session_state:
        st.session_state.selected_workflow_node = "n8n Webhook Trigger"
    if "open_template_id" not in st.session_state:
        st.session_state.open_template_id = "kubernetes-pod-incident-response"
    if "approvals" not in st.session_state:
        st.session_state.approvals = initial_approval_items()
    if "workflow_completed_nodes" not in st.session_state:
        st.session_state.workflow_completed_nodes = []
    if "generated_packages" not in st.session_state:
        st.session_state.generated_packages = {}
    if "demo_runs" not in st.session_state:
        st.session_state.demo_runs = 0
    if "demo_last_stage" not in st.session_state:
        st.session_state.demo_last_stage = "Ready"


def get_incident(incident_id: str | None = None) -> dict[str, Any]:
    target = incident_id or st.session_state.selected_incident_id
    for incident in st.session_state.incidents:
        if incident["id"] == target:
            return incident
    return st.session_state.incidents[0]


def set_selected_incident(incident_id: str) -> None:
    st.session_state.selected_incident_id = incident_id


def update_incident(incident_id: str, **updates: Any) -> None:
    for index, incident in enumerate(st.session_state.incidents):
        if incident["id"] == incident_id:
            updated = dict(incident)
            updated.update(updates)
            st.session_state.incidents[index] = updated
            break


def update_approval(approval_id: str, status: str) -> None:
    for item in st.session_state.approvals:
        if item["id"] == approval_id:
            item["status"] = status
            break


def incident_options() -> dict[str, str]:
    return {f"{incident['id']} - {incident['title']}": incident["id"] for incident in st.session_state.incidents}


def get_ai_for_selected() -> dict[str, Any]:
    return generate_ai_triage(get_incident())


def dashboard_metrics() -> dict[str, Any]:
    incidents = st.session_state.incidents
    pending = sum(1 for item in st.session_state.approvals if item["status"] == "Pending")
    high_risk = sum(1 for item in incidents if item["risk_score"] >= 75)
    generated = sum(1 for item in incidents if item.get("evidence_package_status") == "Generated")
    triaged = sum(1 for item in incidents if item["status"] not in {"New", "Open"})
    return {
        "Total security events": len(incidents),
        "AI-triaged incidents": triaged,
        "High-risk incidents": high_risk,
        "Pending approvals": pending,
        "False-positive reduction": "38%",
        "Mean time to triage": "2.4 min",
        "Automation coverage": "72%",
        "Evidence packages generated": generated + len(st.session_state.generated_packages),
    }
