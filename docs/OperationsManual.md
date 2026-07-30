# Operations & Maintenance Manual

## Monitoring Health Probes

- Liveness: `GET /api/v1/monitoring/liveness`
- Readiness: `GET /api/v1/monitoring/readiness`
- Metrics: `GET /api/v1/monitoring/metrics`

## Incident Report Download API

- HTML/PDF Briefing: `GET /api/v1/reports/incident/{incident_id}/download`
