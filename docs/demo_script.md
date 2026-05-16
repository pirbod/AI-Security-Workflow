# Five-Minute Stakeholder Demo

## 1. Open Dashboard

Start on **Executive Dashboard**. Explain that the PoC shows n8n as the orchestration layer for security operations, not as the detection engine. Point out total events, AI-triaged incidents, high-risk incidents, pending approvals, automation coverage, and evidence packages.

## 2. Run Demo Incident

Open **Demo Mode** and click **Run Demo Incident**. The demo selects a privileged Kubernetes pod creation event, runs it through the workflow stages, approves the simulated high-risk action, generates local evidence packages, and updates dashboard state.

## 3. Show Workflow Canvas

Open **Workflow Canvas**. Select several nodes:

- **n8n Webhook Trigger** for alert intake
- **Normalize Event** for schema mapping
- **AI Agent Triage** for incident reasoning
- **Human Approval** for governance
- **Generate Evidence Package** for audit output

Reinforce that n8n coordinates the workflow while detection sources and downstream systems keep their specialized roles.

## 4. Open AI Agent Panel

Open **AI Agent Panel** with the selected Kubernetes incident. Show the raw alert, normalized event, enrichment summary, deterministic reasoning, confidence score, MITRE-style category, recommended remediation, and evidence references.

## 5. Approve Action

Open **Human Approval Center**. Show that risky actions such as disabling a service account, blocking an IP, or escalating to an incident commander require explicit approval, rejection, or more context.

## 6. Generate Evidence Package

Open **Evidence Package**. Select the incident, preview the report, and generate markdown or JSON. Explain that a production version could store signed artifacts in an evidence repository.

## 7. Explain Production Roadmap

Open **Architecture**. Walk through input sources, n8n orchestration, AI triage, approval governance, output systems, and evidence storage. Close by explaining that production work would replace mock data with real private integrations, durable audit logs, and controlled model access.
