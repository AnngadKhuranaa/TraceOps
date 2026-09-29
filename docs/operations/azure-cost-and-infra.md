# TraceOps Cloud Cost & Operations Framework

## 1. Engineering Budget & Operating Reality

* **Available Azure Credit**: ~$100 (must be treated as a strictly finite engineering budget).
* **Target Development Cost**: **~$5–10/month** during active cloud evaluation.
* **Core Operating Rule**: Local development is the primary development environment (operating at $0 cloud cost). Cloud resources must not be provisioned until local testing is complete and the workload profile is understood.

---

## 2. Cloud Cost Drivers

When running an incident investigation platform on cloud infrastructure, the primary cost drivers are:

1. **Continuous Compute Idle Costs**: Compute services that run 24/7 even when no requests are being processed.
2. **Managed Database Minimum Provisioning**: Managed relational database instances (e.g., Azure Database for PostgreSQL) carry fixed hourly baseline charges regardless of traffic.
3. **Telemetry Ingestion & Analytics Volume**: Azure Monitor / Application Insights charges per gigabyte of ingested log and metric data. Unbounded trace or log collection can exhaust small budgets rapidly.
4. **Log Retention Periods**: Storing multi-gigabyte logs beyond short retention windows compounds storage costs.
5. **LLM API Usage**: Azure OpenAI token consumption scales with prompt length and request frequency.

---

## 3. Cost Control Strategy & Budget Envelopes

To prevent premature consumption of the $100 budget:

### 3.1 Budget Controls & Automated Alerting
* Configure Azure Cost Management budget alerts at **$5.00**, **$8.00**, and **$10.00** monthly thresholds.
* Implement automated alerting or automated shutdown webhooks when thresholds are approached.
* Treat cloud deployments as ephemeral evaluation targets, not permanent staging environments.

### 3.2 Telemetry Limits & Retention Policies
* **Daily Ingestion Cap**: Application Insights daily volume cap enforced at `0.1 GB/day` to prevent billing spikes.
* **Retention Horizon**: Set telemetry retention to the minimum free window (30 days maximum, 7–14 days preferred during dev).
* **Ingestion Sampling**: Filter debug logs and high-frequency health probe telemetry at the ingestion adapter before sending to cloud sinks.

### 3.3 Scale-to-Zero Opportunities
* Prioritize candidate architectures that support zero idle instances (`min_replicas = 0`) when idle.
* If a dedicated virtual machine or non-serverless database is evaluated, it must have an automated shutdown schedule outside working hours.

### 3.4 Bounded LLM Consumption
* Confine LLM usage strictly to the **Explanation** phase.
* Never use LLMs for continuous data scanning, polling, or candidate scoring.
* Bound prompt sizes by sending only pre-filtered evidence graph nodes, not raw log dumps.
* Standardize on compact models (`gpt-4o-mini`) with `max_tokens` limits.

---

## 4. Candidate Cloud Architectures (Deferred Decisions)

No cloud resources are provisioned in Phase 0. The following candidate options will be evaluated once application workload and memory profiles are measured locally:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Candidate Deployment Options (Evaluation Deferred)                     │
├───────────────────────────────────┬────────────────────────────────────┤
│ Compute Candidate                 │ Trade-offs                         │
├───────────────────────────────────┼────────────────────────────────────┤
│ Azure Container Apps (Consumption)│ Pros: Scales to zero, low cost     │
│                                   │ Cons: Cold starts, memory limits   │
├───────────────────────────────────┼────────────────────────────────────┤
│ Azure App Service (Basic/Free)    │ Pros: Simplicity, steady state     │
│                                   │ Cons: Continuous idle cost on Basic│
├───────────────────────────────────┴────────────────────────────────────┤
│ Database Candidate                │ Trade-offs                         │
├───────────────────────────────────┼────────────────────────────────────┤
│ Containerized Postgres on ACA     │ Pros: Very low cost with volume    │
│ with Azure Files storage          │ Cons: Operational burden, no HA    │
├───────────────────────────────────┼────────────────────────────────────┤
│ Azure Database for PostgreSQL     │ Pros: Fully managed, automated backup│
│ Flexible Server (Burstable B1ms)  │ Cons: Baseline fixed hourly cost   │
└───────────────────────────────────┴────────────────────────────────────┘
```

The final cloud runtime and database architecture will be selected via ADR once empirical workload measurements exist.
