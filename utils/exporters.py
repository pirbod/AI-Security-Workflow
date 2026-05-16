"""Evidence package exporters for markdown and JSON artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Template

from utils.mock_ai import build_timeline, generate_ai_triage
from utils.scoring import calculate_risk


OUTPUT_DIR = Path("output")

MARKDOWN_TEMPLATE = Template(
    """# Evidence Package: {{ incident.id }} - {{ incident.title }}

Generated: {{ generated_at }}

## Summary
- Source: {{ incident.source }}
- Severity: {{ incident.severity }}
- Asset: {{ incident.asset }}
- Environment: {{ incident.environment }}
- Risk score: {{ score.risk_score }}
- Confidence score: {{ score.confidence_score }}
- Analyst decision: {{ analyst_decision }}
- Final status: {{ final_status }}

## Timeline
{% for item in timeline -%}
- {{ item.time }}: {{ item.event }}
{% endfor %}

## Raw Alert
{{ incident.raw_alert }}

## Enrichment Results
- Owner: {{ incident.enriched_context.owner }}
- Business service: {{ incident.enriched_context.business_service }}
- Recent changes: {{ incident.enriched_context.recent_changes }}
- Asset tags: {{ incident.enriched_context.asset_tags | join(", ") }}

## AI Summary
{{ ai.reasoning_summary }}

## Risk Explanation
{{ ai.risk_explanation }}

## Recommended Mitigation
{{ ai.recommended_remediation }}

## Evidence References
{% for reference in ai.evidence_references -%}
- {{ reference }}
{% endfor %}
"""
)


def build_evidence_package(
    incident: dict[str, Any],
    analyst_decision: str = "Pending review",
    final_status: str = "Generated for demo review",
) -> dict[str, Any]:
    score = calculate_risk(incident)
    ai = generate_ai_triage(incident)
    return {
        "incident_id": incident["id"],
        "title": incident["title"],
        "timestamp": incident["timestamp"],
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": incident["source"],
        "severity": incident["severity"],
        "asset": incident["asset"],
        "environment": incident["environment"],
        "timeline": build_timeline(incident),
        "raw_alert": incident["raw_alert"],
        "enrichment_results": incident.get("enriched_context", {}),
        "ai_summary": ai["reasoning_summary"],
        "risk_score": score.risk_score,
        "confidence_score": score.confidence_score,
        "analyst_decision": analyst_decision,
        "recommended_mitigation": ai["recommended_remediation"],
        "final_status": final_status,
    }


def render_markdown(incident: dict[str, Any], analyst_decision: str, final_status: str) -> str:
    score = calculate_risk(incident)
    ai = generate_ai_triage(incident)
    return MARKDOWN_TEMPLATE.render(
        incident=incident,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
        score=score,
        ai=ai,
        timeline=build_timeline(incident),
        analyst_decision=analyst_decision,
        final_status=final_status,
    )


def write_markdown_package(incident: dict[str, Any], analyst_decision: str, final_status: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{incident['id'].lower()}_evidence.md"
    path.write_text(render_markdown(incident, analyst_decision, final_status), encoding="utf-8")
    return path


def write_json_package(incident: dict[str, Any], analyst_decision: str, final_status: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{incident['id'].lower()}_evidence.json"
    package = build_evidence_package(incident, analyst_decision, final_status)
    path.write_text(json.dumps(package, indent=2), encoding="utf-8")
    return path
