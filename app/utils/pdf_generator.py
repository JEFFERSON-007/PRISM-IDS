"""Incident Report Generator Utility producing styled HTML/PDF documents."""

from datetime import datetime, timezone
from typing import Any, Dict


class IncidentReportGenerator:
    """Generates styled HTML security briefing documents suitable for PDF conversion."""

    @staticmethod
    def generate_html_report(incident_data: Dict[str, Any]) -> str:
        """Render branded HTML security report for an incident."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        incident_id = incident_data.get("incident_id", "INC-2026-UNKNOWN")
        title = incident_data.get("title", "Security Incident Briefing")
        severity = incident_data.get("severity", "HIGH")
        status = incident_data.get("status", "OPEN")
        description = incident_data.get("description", "No detailed description provided.")

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PRISM IDS Incident Report - {incident_id}</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 40px;
        }}
        .header {{
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .brand {{
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
        }}
        .brand span {{ color: #3b82f6; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            color: #ffffff;
            background-color: #ef4444;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            background-color: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .meta-item label {{
            display: block;
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
        }}
        .meta-item value {{
            font-size: 14px;
            font-weight: bold;
            color: #0f172a;
        }}
        .footer {{
            margin-top: 50px;
            border-top: 1px solid #e2e8f0;
            padding-top: 15px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">PRISM <span>IDS</span> Security Operations</div>
        <div class="badge">{severity} SEVERITY</div>
    </div>

    <div class="section">
        <h1 style="margin:0 0 10px 0; font-size:22px; color:#0f172a;">{title}</h1>
        <p style="font-size:13px; color:#475569;">Incident ID: {incident_id} | Report Generated: {now_str}</p>
    </div>

    <div class="section">
        <div class="section-title">Incident Metadata</div>
        <div class="metadata-grid">
            <div class="meta-item">
                <label>Incident Identifier</label>
                <value>{incident_id}</value>
            </div>
            <div class="meta-item">
                <label>Current Status</label>
                <value>{status}</value>
            </div>
            <div class="meta-item">
                <label>Classification Severity</label>
                <value>{severity}</value>
            </div>
            <div class="meta-item">
                <label>Primary System Target</label>
                <value>Internal Infrastructure Asset</value>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Executive Summary & Description</div>
        <p style="font-size:13px; line-height:1.6; color:#334155;">{description}</p>
    </div>

    <div class="section">
        <div class="section-title">MITRE ATT&CK Framework Mapping</div>
        <ul style="font-size:12px; color:#334155; line-height:1.8;">
            <li><strong>Tactic:</strong> Reconnaissance / Initial Access</li>
            <li><strong>Technique:</strong> T1046 - Network Service Discovery</li>
            <li><strong>Mitigation Strategy:</strong> Enforce perimeter port filtering & rate limiting.</li>
        </ul>
    </div>

    <div class="footer">
        CONFIDENTIAL - PRISM IDS Automated Incident Security Report | Page 1 of 1
    </div>
</body>
</html>"""
