# TraceOps API Guidelines & Design Contracts

## 1. Principles

* **RESTful Resource Orientation**: Use standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`).
* **URL Versioning**: All public endpoints prefixed with `/api/v1/`.
* **Clean Boundary**: API routes act purely as presentation adapters. No business logic or database queries live in routers.

---

## 2. Standard Response & Error Schemas

All error responses strictly adhere to the RFC 7807 **Problem Details** specification:

```json
{
  "type": "https://traceops.dev/errors/incident-not-found",
  "title": "Incident Not Found",
  "status": 404,
  "detail": "Incident 'inc_98234' could not be found.",
  "instance": "/api/v1/incidents/inc_98234",
  "code": "INCIDENT_NOT_FOUND",
  "correlation_id": "c7a8b9f0-2812-4212-b1e8-782a1761e0b1"
}
```

---

## 3. Core Resource Endpoints (Planned)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/incidents` | Register or trigger an incident investigation |
| `GET` | `/api/v1/incidents/{id}` | Retrieve incident state and metadata |
| `GET` | `/api/v1/incidents/{id}/timeline` | Retrieve chronological timeline of changes & anomalies |
| `POST` | `/api/v1/incidents/{id}/analyze` | Trigger root-cause analysis run |
| `GET` | `/api/v1/incidents/{id}/root-cause` | Retrieve ranked candidates, evidence graph, and explanation |
| `POST` | `/api/v1/ingest/changes` | Ingest external change events (webhooks/API) |
| `GET` | `/healthz` | Liveness check (shallow) |
| `GET` | `/readyz` | Readiness check (validates database and essential ports) |
