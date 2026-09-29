# ADR 0003: Core Technology Stack Selection & Evaluation

* **Status**: Accepted (with Cloud Runtime & Production DB explicitly deferred)
* **Date**: 2026-09-29
* **Author**: Principal Software Architect
* **Deciders**: TraceOps Engineering

---

## 1. Context and Problem Statement

The platform requires a robust, modern stack capable of rapid development by a solo engineer, supporting data correlation, statistical analysis, interactive timelines, and local-first development, while keeping eventual development cloud costs within a strict $5–10/month budget using a finite ~$100 credit reserve.

---

## 2. Technology Evaluations & Status

### 2.1 Backend: Python 3.12+ with FastAPI
* **Evaluation**: Python is the standard for data engineering, statistical analysis, and AI/ML ecosystems (NumPy, SciPy, pandas, LLM tooling). FastAPI provides automatic OpenAPI generation, native async support, and high performance.
* **Verdict**: **Adopted**. Standardize on Python 3.12+ and FastAPI. Use `uv` / `ruff` / `mypy` for high-speed dependency resolution, linting, and strict type checking.

### 2.2 Frontend: Next.js (App Router) + TypeScript + Vanilla CSS Tokens
* **Evaluation**: Next.js with TypeScript is the industry benchmark for responsive, rich operational dashboards with server-side rendering and static optimization.
* **Verdict**: **Adopted**. Next.js with React / TypeScript, leveraging Lucide icons and a structured CSS token system for dark-mode operational tooling.

### 2.3 Database: PostgreSQL 16 (Local-First via Docker Compose)
* **Evaluation**: PostgreSQL is exceptionally reliable, handles relational data (incidents, services, changes), supports JSONB for heterogeneous telemetry signals, and supports indexed timestamp ranges.
* **Verdict**:
  - **Adopted Locally**: PostgreSQL 16 managed via `docker-compose.yml` for all local development and integration tests.
  - **Cloud Database Decision DEFERRED**: Do not decide between Azure Database for PostgreSQL Flexible Server, containerized PostgreSQL on container runtimes, or other managed database options until the actual workload, memory footprint, and telemetry write profiles are understood. Do not provision cloud database instances in Phase 0.

### 2.4 Infrastructure as Code: Terraform
* **Evaluation**: Terraform provides declarative multi-cloud capability, ensuring that expanding to AWS or GCP later requires changing IaC modules rather than learning a new tool (like Bicep).
* **Verdict**: **Adopted**. Terraform will be used when cloud resources are eventually provisioned. No cloud resources are provisioned in Phase 0.

### 2.5 Containerization & Orchestration: Docker + Docker Compose
* **Evaluation**: Standard OCI containers ensure parity between macOS local development and production environments.
* **Verdict**: **Adopted**. Multi-stage Dockerfiles for minimal production footprint; Docker Compose for local backing services.

### 2.6 CI/CD: GitHub Actions
* **Evaluation**: Native integration with GitHub repository, fast runner execution, secret management, and matrix testing.
* **Verdict**: **Adopted**.

### 2.7 AI Engine: Azure OpenAI (Strictly bounded)
* **Evaluation**: Confined strictly to synthesis/summarization of verified evidence graphs, not statistical decision making or root-cause ranking.
* **Verdict**: **Adopted as Explanation Adapter**. Use `gpt-4o-mini` with temperature=0 for deterministic narrative generation.

### 2.8 Cloud Runtime: Candidate Deployment Target (Deferred Commitment)
* **Evaluation**: Azure Container Apps (Consumption Plan) is an attractive candidate due to scale-to-zero capabilities. However, committing to ACA prematurely before understanding process memory, background polling characteristics, and container cold starts is unnecessary.
* **Verdict**: **Candidate Target Only (Decision Deferred)**. Azure Container Apps is retained as a candidate deployment target. The final cloud runtime architecture will be selected after the application workload is profiled. Local development remains the primary development environment.

---

## 3. Summary of Decisions

| Layer | Selected Tech | Status |
| :--- | :--- | :--- |
| **Backend** | Python 3.12, FastAPI | Adopted |
| **Frontend** | Next.js, TypeScript | Adopted |
| **Database (Local)** | PostgreSQL 16 (Docker Compose) | Adopted |
| **Database (Cloud)** | Azure Flexible Server vs Containerized Postgres | **DEFERRED** (Evaluate post-workload profiling) |
| **Tooling** | `uv`, `ruff`, `mypy`, `pytest` | Adopted |
| **IaC** | Terraform | Adopted (Provisioning deferred) |
| **Cloud Runtime** | Azure Container Apps | **CANDIDATE ONLY / DEFERRED** |
| **AI Synthesis** | Azure OpenAI (`gpt-4o-mini`) | Adopted (Explanation layer only) |
