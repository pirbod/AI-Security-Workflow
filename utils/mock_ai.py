"""Deterministic mock AI triage responses used by the local demo."""

from __future__ import annotations

from typing import Any

from utils.scoring import calculate_risk


SOURCE_SUMMARIES = {
    "Checkmk": "Infrastructure health signal enriched with service ownership and recent deployment context.",
    "Wazuh": "Endpoint and identity signal enriched with login behavior and account privilege context.",
    "Suricata": "Network detection enriched with asset role, destination rarity, and flow repetition.",
    "Kubernetes": "Cluster event enriched with namespace, service account, deployment window, and workload criticality.",
    "GitHub": "Source-control alert enriched with repository ownership and redacted finding context.",
    "Cloud Audit Logs": "Cloud control-plane event enriched with identity, role, and change-window context.",
    "Gozar Probe": "Access probe event enriched with policy decision path and reliability impact.",
    "CVE Watch": "Vulnerability signal enriched with asset exposure, package context, and remediation SLA.",
}

EVENT_RECOMMENDATIONS = {
    "service_health": "Open a priority incident and capture service, dependency, and change evidence.",
    "suspicious_login": "Require approval before disabling the account and collect login timeline evidence.",
    "network_c2": "Block the suspicious destination after approval and preserve packet metadata.",
    "pod_oom": "Create an engineering ticket with resource trends and restart evidence.",
    "privileged_pod": "Review the workload immediately before disabling the service account or quarantining the pod.",
    "secret_exposure": "Open a security issue, validate whether the value is active, and record remediation.",
    "iam_privilege_escalation": "Escalate to an incident commander and require approval before role rollback.",
    "access_degradation": "Generate an evidence package for access reliability and policy decision review.",
    "cve_detected": "Create a remediation ticket with SLA based on exposure and affected package context.",
    "workload_identity_anomaly": "Confirm the approved test window before marking the activity as false positive.",
}


def normalize_event(incident: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": incident["id"],
        "source": incident["source"],
        "event_type": incident["event_type"],
        "asset": incident["asset"],
        "environment": incident["environment"],
        "observed_at": incident["timestamp"],
        "severity": incident["severity"],
    }


def generate_ai_triage(incident: dict[str, Any]) -> dict[str, Any]:
    """Return a stable, concise triage narrative without calling an LLM."""

    score = calculate_risk(incident)
    source = incident.get("source", "Unknown")
    event_type = incident.get("event_type", "unknown")
    enriched_context = incident.get("enriched_context", {})
    owner = enriched_context.get("owner", "Unknown owner")
    service = enriched_context.get("business_service", "Unknown service")

    if event_type == "privileged_pod":
        reasoning = (
            "The alert is high risk because a privileged Kubernetes pod was created outside "
            "the normal deployment window by a rarely used service account. This should be "
            "reviewed before remediation."
        )
    elif event_type == "iam_privilege_escalation":
        reasoning = (
            "The event changes administrative access on a production cloud project and does "
            "not match an approved change window. Human approval is required before rollback."
        )
    elif event_type == "network_c2":
        reasoning = (
            "The network pattern looks risky because the destination is rare, the sessions are "
            "periodic, and the source asset is part of the production Kubernetes estate."
        )
    elif event_type == "workload_identity_anomaly":
        reasoning = (
            "The activity is unusual but likely explained by a staging load test. Confirm the "
            "test record before closing as a false positive."
        )
    else:
        reasoning = (
            f"The {source} alert is relevant because it affects {service} owned by {owner}. "
            f"The deterministic score places the incident in the {score.severity_label.lower()} risk band."
        )

    return {
        "normalized_event": normalize_event(incident),
        "enrichment_summary": SOURCE_SUMMARIES.get(source, "Alert enriched with asset, identity, and workflow context."),
        "reasoning_summary": reasoning,
        "confidence_score": score.confidence_score,
        "mitre_category": incident.get("mitre_tactic", "Unknown"),
        "recommended_remediation": EVENT_RECOMMENDATIONS.get(event_type, incident.get("recommended_action", "Review incident.")),
        "risk_explanation": score.explanation,
        "evidence_references": [
            f"{incident['id']} raw alert",
            f"{incident['asset']} asset context",
            f"{incident['source']} workflow execution record",
        ],
    }


def build_timeline(incident: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"time": incident["timestamp"], "event": "Alert received through webhook-style intake"},
        {"time": "T+00:30", "event": "Event normalized and routed by workflow type"},
        {"time": "T+01:15", "event": "Asset, identity, network, and CVE context attached"},
        {"time": "T+02:00", "event": "Mock AI triage generated with deterministic confidence score"},
        {"time": "T+02:30", "event": "Risk score calculated and approval decision recorded"},
    ]
