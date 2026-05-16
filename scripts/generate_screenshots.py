from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.mock_ai import generate_ai_triage
from utils.scoring import enrich_incidents_with_scores


WIDTH = 1440
HEIGHT = 950
SIDEBAR = 250
OUT = Path("screenshots")

BG = "#f8fafc"
PANEL = "#ffffff"
BORDER = "#dbe3ef"
TEXT = "#0f172a"
MUTED = "#64748b"
TEAL = "#0f766e"
BLUE = "#2563eb"
ORANGE = "#f97316"
RED = "#dc2626"
AMBER = "#ca8a04"
GREEN = "#16a34a"
VIOLET = "#7c3aed"
CYAN = "#0891b2"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


F12 = font(12)
F13 = font(13)
F14 = font(14)
F15 = font(15)
F16 = font(16)
F18 = font(18, True)
F20 = font(20, True)
F22 = font(22, True)
F30 = font(30, True)


def load_incidents() -> list[dict]:
    return enrich_incidents_with_scores(json.loads(Path("data/mock_incidents.json").read_text(encoding="utf-8")))


def load_templates() -> list[dict]:
    return json.loads(Path("data/workflow_templates.json").read_text(encoding="utf-8"))


def base(page: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, SIDEBAR, HEIGHT), fill="#eef3f8")
    draw.text((28, 28), "AI Security", fill=TEXT, font=F22)
    draw.text((28, 57), "Workflow Orchestrator", fill=TEXT, font=F18)
    nav = [
        "Executive Dashboard",
        "Workflow Canvas",
        "Workflow Templates",
        "Incident Triage",
        "AI Agent Panel",
        "Human Approval Center",
        "Evidence Package",
        "Architecture",
        "Demo Mode",
    ]
    y = 112
    for item in nav:
        active = item == page
        fill = "#dbeafe" if active else "#eef3f8"
        outline = "#93c5fd" if active else "#eef3f8"
        draw.rounded_rectangle((20, y, SIDEBAR - 18, y + 38), radius=8, fill=fill, outline=outline)
        draw.text((34, y + 11), item, fill=BLUE if active else TEXT, font=F14)
        y += 46
    draw.text((28, HEIGHT - 78), "Local PoC", fill=MUTED, font=F13)
    draw.text((28, HEIGHT - 55), "Mock data only", fill=MUTED, font=F13)
    return image, draw


def title(draw: ImageDraw.ImageDraw, page: str, subtitle: str) -> None:
    draw.text((SIDEBAR + 42, 34), page, fill=TEXT, font=F30)
    draw.text((SIDEBAR + 42, 76), subtitle, fill=MUTED, font=F16)


def card(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str = PANEL) -> None:
    draw.rounded_rectangle(xy, radius=10, fill=fill, outline=BORDER, width=1)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, width: int, fill: str = TEXT, fnt=F14, spacing: int = 4) -> int:
    y = xy[1]
    for line in wrap(value, width=width):
        draw.text((xy[0], y), line, fill=fill, font=fnt)
        y += fnt.size + spacing
    return y


def badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, color: str) -> int:
    x, y = xy
    w = int(draw.textlength(value, font=F12)) + 22
    draw.rounded_rectangle((x, y, x + w, y + 24), radius=12, fill="#ffffff", outline=color)
    draw.text((x + 11, y + 6), value, fill=color, font=F12)
    return x + w + 8


def metric(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, label: str, value: str, color: str = TEAL) -> None:
    card(draw, (x, y, x + w, y + 92))
    draw.text((x + 18, y + 16), label.upper(), fill=MUTED, font=F12)
    draw.text((x + 18, y + 44), value, fill=color, font=F30)


def bar_chart(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title_value: str, data: dict[str, int], colors: list[str]) -> None:
    card(draw, (x, y, x + w, y + h))
    draw.text((x + 18, y + 16), title_value, fill=TEXT, font=F18)
    max_value = max(data.values()) if data else 1
    chart_y = y + 58
    bar_h = 26
    for index, (label, value) in enumerate(data.items()):
        yy = chart_y + index * 42
        draw.text((x + 18, yy + 5), label[:24], fill=TEXT, font=F13)
        bar_x = x + 190
        bar_w = int((w - 250) * value / max_value)
        draw.rounded_rectangle((bar_x, yy, bar_x + bar_w, yy + bar_h), radius=6, fill=colors[index % len(colors)])
        draw.text((bar_x + bar_w + 10, yy + 5), str(value), fill=MUTED, font=F13)


def pie(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title_value: str, data: dict[str, int], colors: list[str]) -> None:
    card(draw, (x, y, x + w, y + h))
    draw.text((x + 18, y + 16), title_value, fill=TEXT, font=F18)
    total = sum(data.values()) or 1
    box = (x + 38, y + 70, x + 238, y + 270)
    start = 0
    for index, (label, value) in enumerate(data.items()):
        extent = 360 * value / total
        draw.pieslice(box, start=start, end=start + extent, fill=colors[index % len(colors)])
        start += extent
        yy = y + 80 + index * 30
        draw.rectangle((x + 285, yy, x + 303, yy + 18), fill=colors[index % len(colors)])
        draw.text((x + 314, yy), f"{label}: {value}", fill=TEXT, font=F13)
    draw.ellipse((x + 88, y + 120, x + 188, y + 220), fill=PANEL)


def table(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, rows: list[list[str]], columns: list[str], row_h: int = 36) -> None:
    h = 42 + row_h * len(rows)
    card(draw, (x, y, x + w, y + h))
    col_w = w // len(columns)
    for i, col in enumerate(columns):
        draw.text((x + 16 + i * col_w, y + 14), col, fill=MUTED, font=F12)
    yy = y + 42
    for row in rows:
        draw.line((x + 12, yy, x + w - 12, yy), fill="#edf2f7")
        for i, value in enumerate(row):
            draw.text((x + 16 + i * col_w, yy + 10), str(value)[:22], fill=TEXT, font=F13)
        yy += row_h


def save(image: Image.Image, filename: str) -> None:
    optimized = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    optimized.save(OUT / filename, optimize=True)


def dashboard() -> None:
    incidents = load_incidents()
    image, draw = base("Executive Dashboard")
    title(draw, "AI Security Workflow Orchestrator", "Executive view of n8n-orchestrated AI-native security workflows.")
    metrics = [
        ("Total security events", str(len(incidents)), BLUE),
        ("AI-triaged incidents", "10", TEAL),
        ("High-risk incidents", str(sum(1 for i in incidents if i["risk_score"] >= 75)), RED),
        ("Pending approvals", "6", AMBER),
        ("False-positive reduction", "38%", GREEN),
        ("Mean time to triage", "2.4m", VIOLET),
        ("Automation coverage", "72%", CYAN),
        ("Evidence packages", "3", ORANGE),
    ]
    x0 = SIDEBAR + 42
    y0 = 126
    for idx, item in enumerate(metrics):
        metric(draw, x0 + (idx % 4) * 286, y0 + (idx // 4) * 112, 264, item[0], item[1], item[2])
    counts = Counter(i["source"] for i in incidents)
    severities = Counter(i["severity"] for i in incidents)
    bar_chart(draw, x0, 370, 548, 275, "Incidents by source", dict(counts.most_common(5)), [BLUE, TEAL, ORANGE, VIOLET, CYAN])
    pie(draw, x0 + 584, 370, 548, 275, "Incidents by severity", dict(severities), [RED, ORANGE, AMBER, GREEN])
    rows = [[f"WF-{1000+i}", inc["source"], inc["severity"], inc["risk_score"], inc["status"]] for i, inc in enumerate(incidents[:6])]
    table(draw, x0, 680, 1132, rows, ["Execution ID", "Source", "Severity", "Risk", "Status"])
    save(image, "01_dashboard.png")


def workflow_canvas() -> None:
    image, draw = base("Workflow Canvas")
    title(draw, "Workflow Canvas", "n8n-style orchestration path from alert intake to evidence generation.")
    nodes = [
        "Security Event Source",
        "n8n Webhook Trigger",
        "Normalize Event",
        "Enrich Asset Context",
        "Enrich CVE Context",
        "AI Agent Triage",
        "Risk Score",
        "Human Approval",
        "Create Ticket",
        "Notify Teams or Slack",
        "Generate Evidence Package",
    ]
    x0 = SIDEBAR + 44
    y0 = 132
    positions = []
    for idx, name in enumerate(nodes):
        x = x0
        y = y0 + idx * 64
        positions.append((x, y))
        fill = "#e0f2fe" if idx != 5 else "#ffedd5"
        outline = BLUE if idx != 5 else ORANGE
        card(draw, (x, y, x + 560, y + 48), fill=fill)
        draw.rounded_rectangle((x, y, x + 560, y + 48), radius=10, outline=outline, width=2)
        draw.text((x + 18, y + 15), name, fill=TEXT, font=F14)
        draw.text((x + 360, y + 15), "completed", fill=GREEN, font=F13)
    for idx in range(len(positions) - 1):
        x1, y1 = positions[idx]
        x2, y2 = positions[idx + 1]
        draw.line((x1 + 280, y1 + 48, x2 + 280, y2), fill="#94a3b8", width=2)
        draw.polygon([(x2 + 280, y2), (x2 + 274, y2 - 8), (x2 + 286, y2 - 8)], fill="#94a3b8")
    panel_x = SIDEBAR + 672
    card(draw, (panel_x, 146, 1390, 760))
    draw.text((panel_x + 22, 168), "AI Agent Triage", fill=TEXT, font=F22)
    badge(draw, (panel_x + 22, 205), "AI Agent", ORANGE)
    detail = [
        ("Purpose", "Produces concise reasoning, category, and remediation guidance from enriched context."),
        ("Input example", '{"incident": "enriched event"}'),
        ("Output example", '{"summary": "high-risk privileged action", "confidence": 95}'),
        ("Security value", "Gives analysts a compact first-pass narrative without making final decisions."),
        ("Failure handling", "Fall back to deterministic templates and require human review."),
    ]
    yy = 248
    for label, value in detail:
        draw.text((panel_x + 22, yy), label, fill=MUTED, font=F13)
        yy = text(draw, (panel_x + 22, yy + 21), value, 72, TEXT, F14) + 16
    save(image, "02_workflow_canvas.png")


def incident_triage() -> None:
    incidents = load_incidents()
    selected = next(i for i in incidents if i["id"] == "INC-1005")
    image, draw = base("Incident Triage")
    title(draw, "Incident Triage", "Mock enriched incidents ready for AI triage and workflow routing.")
    x0 = SIDEBAR + 42
    filters = ["All", "Critical", "High", "Needs approval", "Auto-resolved", "False positive", "Evidence generated"]
    x = x0
    for idx, item in enumerate(filters):
        x = badge(draw, (x, 126), item, TEAL if idx == 0 else MUTED)
    for idx, incident in enumerate(incidents[:6]):
        y = 174 + idx * 96
        card(draw, (x0, y, x0 + 520, y + 78))
        draw.text((x0 + 18, y + 14), f"{incident['id']} · {incident['title']}", fill=TEXT, font=F16)
        bx = badge(draw, (x0 + 18, y + 44), incident["severity"], RED if incident["severity"] == "Critical" else ORANGE if incident["severity"] == "High" else AMBER)
        badge(draw, (bx, y + 44), incident["source"], BLUE)
        draw.text((x0 + 380, y + 46), f"Risk {incident['risk_score']}", fill=MUTED, font=F13)
    card(draw, (x0 + 560, 174, 1390, 760))
    draw.text((x0 + 584, 202), f"{selected['id']} · {selected['title']}", fill=TEXT, font=F22)
    bx = badge(draw, (x0 + 584, 244), selected["severity"], RED)
    bx = badge(draw, (bx, 244), f"Risk {selected['risk_score']}", TEAL)
    badge(draw, (bx, 244), f"Confidence {selected['confidence_score']}", BLUE)
    y = text(draw, (x0 + 584, 292), selected["raw_alert"], 84, TEXT, F15)
    details = [
        ("Source", selected["source"]),
        ("Asset", selected["asset"]),
        ("Environment", selected["environment"]),
        ("MITRE-style tactic", selected["mitre_tactic"]),
        ("Recommended action", selected["recommended_action"]),
        ("Status", selected["status"]),
        ("Approval required", "Yes"),
        ("Ticket status", selected["ticket_status"]),
        ("Evidence package status", selected["evidence_package_status"]),
    ]
    yy = y + 26
    for label, value in details:
        draw.text((x0 + 584, yy), label, fill=MUTED, font=F13)
        draw.text((x0 + 760, yy), str(value)[:66], fill=TEXT, font=F13)
        yy += 30
    save(image, "03_incident_triage.png")


def ai_agent_panel() -> None:
    incident = next(i for i in load_incidents() if i["id"] == "INC-1005")
    ai = generate_ai_triage(incident)
    image, draw = base("AI Agent Panel")
    title(draw, "AI Agent Panel", "Deterministic mock AI triage output from enriched workflow context.")
    x0 = SIDEBAR + 42
    metric(draw, x0, 126, 250, "Risk score", str(incident["risk_score"]), RED)
    metric(draw, x0 + 278, 126, 250, "Confidence", str(ai["confidence_score"]), TEAL)
    metric(draw, x0 + 556, 126, 330, "MITRE-style category", ai["mitre_category"], VIOLET)
    card(draw, (x0, 258, x0 + 548, 560))
    draw.text((x0 + 22, 282), "Raw Alert", fill=TEXT, font=F20)
    text(draw, (x0 + 22, 322), incident["raw_alert"], 66, TEXT, F15)
    draw.text((x0 + 22, 440), "Enrichment Summary", fill=TEXT, font=F18)
    text(draw, (x0 + 22, 474), ai["enrichment_summary"], 66, TEXT, F14)
    card(draw, (x0 + 584, 258, 1390, 560))
    draw.text((x0 + 608, 282), "Normalized Event", fill=TEXT, font=F18)
    yy = 322
    for key, value in ai["normalized_event"].items():
        draw.text((x0 + 608, yy), f"{key}: ", fill=MUTED, font=F14)
        draw.text((x0 + 780, yy), str(value), fill=TEXT, font=F14)
        yy += 30
    card(draw, (x0, 596, x0 + 548, 832))
    draw.text((x0 + 22, 620), "AI Reasoning Summary", fill=TEXT, font=F18)
    text(draw, (x0 + 22, 660), ai["reasoning_summary"], 64, TEXT, F15)
    card(draw, (x0 + 584, 596, 1390, 832))
    draw.text((x0 + 608, 620), "Recommended Remediation", fill=TEXT, font=F18)
    text(draw, (x0 + 608, 660), ai["recommended_remediation"], 64, TEXT, F15)
    draw.text((x0 + 608, 746), "Evidence References", fill=TEXT, font=F18)
    yy = 780
    for ref in ai["evidence_references"]:
        draw.text((x0 + 608, yy), f"- {ref}", fill=MUTED, font=F14)
        yy += 26
    save(image, "04_ai_agent_panel.png")


def approval_center() -> None:
    image, draw = base("Human Approval Center")
    title(draw, "Human Approval Center", "Governance layer for high-impact security actions.")
    approvals = [
        ("Restart Kubernetes pod", "INC-1004", "Medium", "Pending", "Production workload restart can affect payment processing."),
        ("Block suspicious IP", "INC-1003", "High", "Pending", "Blocking traffic may affect a legitimate integration."),
        ("Disable service account", "INC-1005", "Critical", "Approved", "Service account can create privileged workloads in production."),
        ("Create high-priority incident ticket", "INC-1001", "Critical", "Pending", "Checkout service is degraded."),
        ("Escalate to incident commander", "INC-1007", "Critical", "Pending", "Administrative role changed in cloud IAM."),
        ("Trigger forensic evidence collection", "INC-1003", "High", "Pending", "Potential C2 traffic requires preserved network evidence."),
        ("Open GitHub security issue", "INC-1006", "High", "Pending", "Finding should be tracked without exposing sensitive values."),
    ]
    x0 = SIDEBAR + 42
    metric(draw, x0, 126, 270, "Pending approvals", "6", AMBER)
    y = 252
    for idx, item in enumerate(approvals):
        x = x0 + (idx % 2) * 572
        yy = y + (idx // 2) * 142
        card(draw, (x, yy, x + 540, yy + 118))
        draw.text((x + 18, yy + 16), item[0], fill=TEXT, font=F18)
        badge(draw, (x + 18, yy + 48), item[2], RED if item[2] == "Critical" else ORANGE if item[2] == "High" else AMBER)
        badge(draw, (x + 110, yy + 48), item[3], GREEN if item[3] == "Approved" else AMBER)
        draw.text((x + 18, yy + 82), f"{item[1]} · {item[4]}", fill=MUTED, font=F13)
    save(image, "05_approval_center.png")


def evidence_package() -> None:
    incident = next(i for i in load_incidents() if i["id"] == "INC-1005")
    ai = generate_ai_triage(incident)
    image, draw = base("Evidence Package")
    title(draw, "Evidence Package", "Local markdown and JSON evidence records for audit-ready handoff.")
    x0 = SIDEBAR + 42
    metric(draw, x0, 126, 250, "Incident", incident["id"], BLUE)
    metric(draw, x0 + 278, 126, 250, "Severity", incident["severity"], RED)
    metric(draw, x0 + 556, 126, 250, "Risk", str(incident["risk_score"]), ORANGE)
    metric(draw, x0 + 834, 126, 250, "Confidence", str(incident["confidence_score"]), TEAL)
    card(draw, (x0, 258, 1390, 840))
    draw.text((x0 + 28, 286), f"Evidence Package: {incident['id']} - {incident['title']}", fill=TEXT, font=F22)
    y = 336
    sections = [
        ("Summary", f"Source: {incident['source']} · Asset: {incident['asset']} · Environment: {incident['environment']}"),
        ("Timeline", "Alert received · Normalized · Enriched · AI triaged · Risk scored · Approval recorded"),
        ("Raw Alert", incident["raw_alert"]),
        ("AI Summary", ai["reasoning_summary"]),
        ("Recommended Mitigation", ai["recommended_remediation"]),
        ("Final Status", "Generated for demo review"),
    ]
    for label, value in sections:
        draw.text((x0 + 28, y), label, fill=TEAL, font=F18)
        y = text(draw, (x0 + 28, y + 30), value, 126, TEXT, F14) + 18
    save(image, "06_evidence_package.png")


def architecture() -> None:
    image, draw = base("Architecture")
    title(draw, "Architecture", "Target operating model for n8n-orchestrated AI security workflows.")
    layers = [
        ("Input Sources", ["Checkmk", "Wazuh", "Suricata", "Kubernetes", "Cloud audit logs", "GitHub", "Gozar probes", "CVE feeds"], BLUE),
        ("n8n Orchestration Layer", ["Webhook intake", "Workflow routing", "Enrichment", "AI agent call", "Risk scoring", "Human approval", "Ticketing", "Notification", "Evidence packaging"], TEAL),
        ("AI Triage Layer", ["Local LLM compatible interface", "Incident memory", "Vector search placeholder", "Deterministic PoC scoring", "Future RAG capability"], VIOLET),
        ("Approval and Governance", ["Manual approvals", "Action records", "Policy gates", "Decision history"], ORANGE),
        ("Output Systems", ["Jira", "ServiceNow", "Slack", "Microsoft Teams", "GitHub Issues", "SIEM"], CYAN),
        ("Evidence and Audit Layer", ["Markdown evidence package", "JSON evidence package", "Timeline", "Risk explanation"], GREEN),
    ]
    x0 = SIDEBAR + 42
    for idx, (name, items, color) in enumerate(layers):
        x = x0 + (idx % 3) * 376
        y = 148 + (idx // 3) * 230
        card(draw, (x, y, x + 346, y + 178))
        draw.rectangle((x, y, x + 346, y + 8), fill=color)
        draw.text((x + 20, y + 28), name, fill=TEXT, font=F18)
        text(draw, (x + 20, y + 68), " · ".join(items), 42, MUTED, F14)
    arrows = [(x0 + 346, 237, x0 + 376, 237), (x0 + 722, 237, x0 + 752, 237), (x0 + 346, 467, x0 + 376, 467), (x0 + 722, 467, x0 + 752, 467)]
    for x1, y1, x2, y2 in arrows:
        draw.line((x1, y1, x2, y2), fill="#94a3b8", width=3)
        draw.polygon([(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)], fill="#94a3b8")
    card(draw, (x0, 660, 1390, 812))
    draw.text((x0 + 24, 686), "Operating Principle", fill=TEXT, font=F22)
    text(
        draw,
        (x0 + 24, 730),
        "Detection sources create alerts. n8n coordinates enrichment, AI triage, approval, ticketing, notification, and evidence packaging. Risky actions remain governed by human decision records.",
        132,
        TEXT,
        F16,
    )
    save(image, "07_architecture.png")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    dashboard()
    workflow_canvas()
    incident_triage()
    ai_agent_panel()
    approval_center()
    evidence_package()
    architecture()


if __name__ == "__main__":
    main()
