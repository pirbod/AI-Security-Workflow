from __future__ import annotations

import json

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_agraph import Config, Edge, Node, agraph

    HAS_AGRAPH = True
except Exception:
    HAS_AGRAPH = False


WORKFLOW_NODES = [
    {
        "name": "Security Event Source",
        "type": "Detection source",
        "purpose": "Represents Checkmk, Wazuh, Suricata, Kubernetes, GitHub, cloud audit logs, Gozar probes, or CVE feeds.",
        "input": {"alert": "source-native event"},
        "output": {"webhook_payload": "normalized intake candidate"},
        "security_value": "Keeps detection ownership separate from orchestration.",
        "failure_handling": "Retry intake or hold event in source queue.",
    },
    {
        "name": "n8n Webhook Trigger",
        "type": "Webhook Trigger",
        "purpose": "Receives alert payloads from security tools through webhook-style intake.",
        "input": {"source": "Kubernetes", "event": "privileged_pod"},
        "output": {"execution_id": "WF-1005", "payload": "accepted"},
        "security_value": "Creates a standard entry point for heterogeneous detections.",
        "failure_handling": "Return non-success response and preserve failed payload metadata.",
    },
    {
        "name": "Normalize Event",
        "type": "Code Node",
        "purpose": "Maps source-specific fields to a consistent incident schema.",
        "input": {"namespace": "payments", "securityContext": "privileged"},
        "output": {"event_type": "privileged_pod", "asset": "prod-cluster-a"},
        "security_value": "Reduces analyst time spent decoding source-specific payloads.",
        "failure_handling": "Route malformed events to a review queue.",
    },
    {
        "name": "Enrich Asset Context",
        "type": "HTTP Request",
        "purpose": "Looks up asset owner, environment, criticality, and service tags.",
        "input": {"asset": "prod-cluster-a"},
        "output": {"owner": "Cloud Platform", "criticality": "critical"},
        "security_value": "Connects risk to business impact and ownership.",
        "failure_handling": "Continue with unknown owner and lower confidence.",
    },
    {
        "name": "Enrich CVE Context",
        "type": "HTTP Request",
        "purpose": "Adds vulnerability context when the alert references affected packages or services.",
        "input": {"asset": "inventory-api-03", "package": "mock-http-runtime"},
        "output": {"cve": "CVE-2026-1842", "recommended_sla": "72 hours"},
        "security_value": "Prioritizes vulnerability work by exposure and context.",
        "failure_handling": "Flag CVE lookup as unavailable and proceed with asset-only scoring.",
    },
    {
        "name": "AI Agent Triage",
        "type": "AI Agent",
        "purpose": "Produces concise reasoning, category, and remediation guidance from enriched context.",
        "input": {"incident": "enriched event"},
        "output": {"summary": "high-risk privileged action", "confidence": 95},
        "security_value": "Gives analysts a compact first-pass narrative without making final decisions.",
        "failure_handling": "Fall back to deterministic templates and require human review.",
    },
    {
        "name": "Risk Score",
        "type": "Code Node",
        "purpose": "Applies deterministic scoring across severity, exposure, identity, CVE, and repetition signals.",
        "input": {"severity": "Critical", "environment": "Production", "privileged_action": True},
        "output": {"risk_score": 100, "approval_required": True},
        "security_value": "Makes triage consistent and explainable.",
        "failure_handling": "Use conservative default and mark confidence low.",
    },
    {
        "name": "Human Approval",
        "type": "Manual Approval",
        "purpose": "Pauses risky remediation until an analyst approves, rejects, or requests more context.",
        "input": {"action": "Disable service account", "risk": "Critical"},
        "output": {"decision": "Approved", "approver": "demo analyst"},
        "security_value": "Keeps high-impact actions governed and auditable.",
        "failure_handling": "Escalate after timeout and keep action pending.",
    },
    {
        "name": "Create Ticket",
        "type": "Jira or ServiceNow output",
        "purpose": "Creates or updates a tracked incident, vulnerability, or engineering ticket.",
        "input": {"priority": "P1", "owner": "Cloud Platform"},
        "output": {"ticket": "SEC-DEMO-1042", "status": "Created"},
        "security_value": "Turns alert context into accountable remediation work.",
        "failure_handling": "Queue retry and notify operations channel.",
    },
    {
        "name": "Notify Teams or Slack",
        "type": "Slack or Teams output",
        "purpose": "Sends a concise status update to the responsible response channel.",
        "input": {"incident": "INC-1005", "ticket": "SEC-DEMO-1042"},
        "output": {"channel": "security-operations", "message": "posted"},
        "security_value": "Keeps stakeholders informed without exposing sensitive payloads.",
        "failure_handling": "Log notification failure and keep ticket as source of truth.",
    },
    {
        "name": "Generate Evidence Package",
        "type": "File generation",
        "purpose": "Builds markdown and JSON evidence records for review, audit, and handoff.",
        "input": {"incident": "INC-1005", "decision": "Approved"},
        "output": {"markdown": "output/inc-1005_evidence.md", "json": "output/inc-1005_evidence.json"},
        "security_value": "Preserves a repeatable decision trail for security operations.",
        "failure_handling": "Retry file generation and keep package status incomplete.",
    },
]

WORKFLOW_EDGES = [(WORKFLOW_NODES[index]["name"], WORKFLOW_NODES[index + 1]["name"]) for index in range(len(WORKFLOW_NODES) - 1)]


def _node_by_name(name: str) -> dict:
    return next(node for node in WORKFLOW_NODES if node["name"] == name)


def _render_plotly_graph() -> None:
    graph = nx.DiGraph()
    graph.add_nodes_from([node["name"] for node in WORKFLOW_NODES])
    graph.add_edges_from(WORKFLOW_EDGES)
    positions = {node["name"]: (index % 4, -(index // 4)) for index, node in enumerate(WORKFLOW_NODES)}

    edge_x, edge_y = [], []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [positions[node["name"]][0] for node in WORKFLOW_NODES]
    node_y = [positions[node["name"]][1] for node in WORKFLOW_NODES]
    labels = [node["name"] for node in WORKFLOW_NODES]
    colors = ["#0f766e" if label == st.session_state.selected_workflow_node else "#2563eb" for label in labels]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=2, color="#94a3b8"), hoverinfo="skip"))
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="bottom center",
            marker=dict(size=34, color=colors, line=dict(width=2, color="#e2e8f0")),
            customdata=labels,
            hovertemplate="%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        height=520,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points", key="workflow_plot")
    if event and event.selection.points:
        st.session_state.selected_workflow_node = event.selection.points[0]["customdata"]


def _render_agraph() -> None:
    nodes = []
    completed = set(st.session_state.workflow_completed_nodes)
    for node in WORKFLOW_NODES:
        color = "#0f766e" if node["name"] in completed else "#2563eb"
        if node["name"] == st.session_state.selected_workflow_node:
            color = "#f97316"
        nodes.append(Node(id=node["name"], label=node["name"], size=24, color=color))

    edges = [Edge(source=source, target=target, type="CURVE_SMOOTH") for source, target in WORKFLOW_EDGES]
    config = Config(
        width="100%",
        height=500,
        directed=True,
        physics=False,
        hierarchical=True,
        nodeHighlightBehavior=True,
        highlightColor="#f97316",
        collapsible=False,
    )
    selected = agraph(nodes=nodes, edges=edges, config=config)
    if isinstance(selected, str):
        st.session_state.selected_workflow_node = selected


def render() -> None:
    st.markdown('<div class="app-title">Workflow Canvas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">n8n-style orchestration path from alert intake to evidence package generation.</div>',
        unsafe_allow_html=True,
    )

    graph_col, detail_col = st.columns([1.45, 1])
    with graph_col:
        st.caption("Select a node in the graph or use the selector below.")
        if HAS_AGRAPH:
            _render_agraph()
        else:
            _render_plotly_graph()

        node_names = [node["name"] for node in WORKFLOW_NODES]
        selected = st.selectbox(
            "Workflow node",
            node_names,
            index=node_names.index(st.session_state.selected_workflow_node),
        )
        st.session_state.selected_workflow_node = selected

    with detail_col:
        node = _node_by_name(st.session_state.selected_workflow_node)
        st.subheader(node["name"])
        st.markdown(f'<span class="badge badge-neutral">{node["type"]}</span>', unsafe_allow_html=True)
        st.write(node["purpose"])
        st.markdown("**Input example**")
        st.code(json.dumps(node["input"], indent=2), language="json")
        st.markdown("**Output example**")
        st.code(json.dumps(node["output"], indent=2), language="json")
        st.markdown("**Security value**")
        st.write(node["security_value"])
        st.markdown("**Failure handling**")
        st.write(node["failure_handling"])
