from __future__ import annotations

import streamlit as st

from components import (
    ai_agent_panel,
    approval_center,
    architecture,
    dashboard,
    demo_mode,
    evidence_package,
    incident_triage,
    workflow_canvas,
    workflow_templates,
)
from utils.state import initialize_state


PAGES = {
    "Executive Dashboard": dashboard.render,
    "Workflow Canvas": workflow_canvas.render,
    "Workflow Templates": workflow_templates.render,
    "Incident Triage": incident_triage.render,
    "AI Agent Panel": ai_agent_panel.render,
    "Human Approval Center": approval_center.render,
    "Evidence Package": evidence_package.render,
    "Architecture": architecture.render,
    "Demo Mode": demo_mode.render,
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --panel-border: rgba(148, 163, 184, 0.28);
            --muted-copy: #64748b;
            --accent: #0f766e;
            --accent-soft: rgba(15, 118, 110, 0.12);
            --risk-critical: #dc2626;
            --risk-high: #ea580c;
            --risk-medium: #ca8a04;
            --risk-low: #16a34a;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1360px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid var(--panel-border);
        }

        .app-title {
            font-size: 1.85rem;
            line-height: 1.15;
            font-weight: 760;
            margin-bottom: 0.15rem;
        }

        .app-subtitle {
            color: var(--muted-copy);
            font-size: 0.98rem;
            margin-bottom: 1.25rem;
        }

        .metric-card, .info-card, .template-card, .stage-card {
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.02);
            min-height: 100%;
        }

        .metric-label {
            color: var(--muted-copy);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            font-size: 1.65rem;
            font-weight: 760;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border: 1px solid var(--panel-border);
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 650;
            margin-right: 0.35rem;
            white-space: nowrap;
        }

        .badge-critical { color: var(--risk-critical); background: rgba(220, 38, 38, 0.10); }
        .badge-high { color: var(--risk-high); background: rgba(234, 88, 12, 0.10); }
        .badge-medium { color: var(--risk-medium); background: rgba(202, 138, 4, 0.10); }
        .badge-low { color: var(--risk-low); background: rgba(22, 163, 74, 0.10); }
        .badge-neutral { color: var(--accent); background: var(--accent-soft); }

        .small-muted {
            color: var(--muted-copy);
            font-size: 0.86rem;
        }

        .section-caption {
            color: var(--muted-copy);
            font-size: 0.92rem;
            margin-top: -0.35rem;
            margin-bottom: 0.8rem;
        }

        div[data-testid="stButton"] > button {
            border-radius: 8px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="AI Security Workflow Orchestrator",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    initialize_state()

    st.sidebar.markdown("### AI Security Workflow Orchestrator")
    page = st.sidebar.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.caption("Local PoC using mock security data. n8n is represented as the workflow orchestration layer.")

    PAGES[page]()


if __name__ == "__main__":
    main()
