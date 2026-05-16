"""Deterministic incident scoring for the local PoC."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScoreResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)
    approval_required: bool
    severity_label: str
    explanation: str


BASE_SEVERITY = {
    "Critical": 70,
    "High": 55,
    "Medium": 35,
    "Low": 20,
}


def _has_known_cve(value: Any) -> bool:
    return bool(value and str(value).lower() not in {"none", "n/a", "null"})


def _severity_from_score(score: int) -> str:
    if score >= 85:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def calculate_risk(incident: dict[str, Any]) -> ScoreResult:
    """Return a reproducible risk score and approval decision for a mock incident."""

    severity = str(incident.get("severity", "Medium")).title()
    score = BASE_SEVERITY.get(severity, 35)
    reasons = [f"{severity} base severity starts at {score}"]

    criticality = str(incident.get("asset_criticality", "")).lower()
    if criticality == "critical":
        score += 10
        reasons.append("critical asset adds 10")
    elif criticality == "high":
        score += 6
        reasons.append("high-value asset adds 6")

    if str(incident.get("environment", "")).lower() == "production":
        score += 10
        reasons.append("production environment adds 10")

    if _has_known_cve(incident.get("cve_context")):
        score += 8
        reasons.append("known CVE context adds 8")

    repeated_count = int(incident.get("repeated_count") or 0)
    if repeated_count:
        repeated_points = min(10, max(0, repeated_count))
        score += repeated_points
        reasons.append(f"repeated activity adds {repeated_points}")

    identity_context = str(incident.get("identity_context", "")).lower()
    if "privileged" in identity_context or "rarely used" in identity_context:
        score += 8
        reasons.append("identity risk adds 8")

    if bool(incident.get("internet_exposed")):
        score += 7
        reasons.append("internet exposure adds 7")

    if bool(incident.get("privileged_action")):
        score += 10
        reasons.append("privileged action adds 10")

    if bool(incident.get("external_ip_indicator")):
        score += 5
        reasons.append("external IP indicator adds 5")

    score = min(100, max(0, score))
    confidence = 62
    confidence += 8 if incident.get("raw_alert") else 0
    confidence += 8 if incident.get("enriched_context") else 0
    confidence += 7 if incident.get("asset_criticality") else 0
    confidence += 5 if incident.get("network_context") else 0
    confidence += 5 if incident.get("identity_context") else 0
    confidence += min(5, repeated_count)
    confidence = min(98, confidence)

    approval_required = score >= 75 or bool(incident.get("privileged_action"))
    severity_label = _severity_from_score(score)

    return ScoreResult(
        risk_score=score,
        confidence_score=confidence,
        approval_required=approval_required,
        severity_label=severity_label,
        explanation="; ".join(reasons) + f"; final risk score is {score}.",
    )


def enrich_incident_with_score(incident: dict[str, Any]) -> dict[str, Any]:
    scored = dict(incident)
    result = calculate_risk(scored)
    scored.update(result.model_dump())
    return scored


def enrich_incidents_with_scores(incidents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_incident_with_score(incident) for incident in incidents]
