# Architecture Notes

## Why n8n Is The Orchestration Layer

n8n is positioned as the automation layer that coordinates work after a detection source emits an alert. It receives webhook-style intake, normalizes payloads, enriches context, calls scoring and triage logic, routes approval decisions, creates tickets, sends notifications, and triggers evidence packaging.

This separation keeps detection logic in the tools that specialize in detection:

- Checkmk detects service health and infrastructure issues.
- Wazuh detects endpoint and identity-related activity.
- Suricata detects network events.
- Kubernetes emits workload and audit events.
- GitHub emits source-control security events.
- Cloud audit logs emit identity and control-plane changes.
- CVE feeds provide vulnerability context.
- Access probes provide reliability and access-control evidence.

## Why Python Handles Scoring And Mock AI

Python is used for the local PoC because it is easy to run, easy to inspect, and suitable for deterministic security logic. The scoring module gives each incident an explainable risk score using severity, asset criticality, production exposure, known CVE context, repetition, identity risk, privileged actions, and external indicators.

The mock AI module does not call an LLM. It returns deterministic triage summaries that show what an AI layer could produce in a production system while keeping the demo fully local and safe.

## Mapping To Real SOC Operations

The workflow maps to a practical SOC pattern:

1. Alert arrives from a detection source.
2. n8n starts a workflow through webhook-style intake.
3. The event is normalized into a common incident schema.
4. Enrichment attaches asset, identity, network, CVE, and ownership context.
5. AI triage produces a concise analyst-ready summary.
6. Deterministic scoring decides whether approval is required.
7. Human approval gates risky remediation.
8. Tickets and notifications route work to accountable teams.
9. Evidence packages preserve the alert, context, reasoning, decision, and mitigation path.

## Future Production Path

A production implementation would keep the same boundaries but replace mock components:

- n8n production workflows for webhook intake, enrichment, routing, and outputs.
- Private enrichment sources such as CMDB, IAM, SIEM, vulnerability management, and Kubernetes APIs.
- A local or approved private AI model interface with redaction and prompt governance.
- Durable audit storage for workflow execution and approval decisions.
- Signed evidence packages with retention policy.
- Schema validation for every source payload.
- Access control for approval actions and evidence downloads.
