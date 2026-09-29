# TraceOps

> Cloud incident investigation and root-cause intelligence platform.

TraceOps answers the critical engineering question:  
**"What changed before my application broke, and which change is most likely responsible?"**

---

## Architecture Overview

TraceOps is architected as a **Modular Monolith** applying **Clean Architecture** and **Hexagonal Architecture (Ports and Adapters)** principles. It strictly isolates pure domain rules from infrastructure technologies (Azure, PostgreSQL, LLMs, GitHub), ensuring long-term maintainability, deterministic testability, and cloud portability.

### Key Architecture Tenets
1. **Protected Domain**: The domain layer contains zero external dependencies (no FastAPI, no SQLAlchemy/PostgreSQL, no Pydantic, no Azure SDKs, no OpenAI SDKs).
2. **Four Cognitive Pillars**: Strict conceptual separation between **Facts** (immutable observations), **Hypotheses** (candidate root causes), **Evidence** (deterministic metrics and relationships), and **Explanations** (human-readable synthesis).
3. **Deterministic-First Root Cause Engine**: Candidates, scores, and evidence graphs are generated deterministically through statistical and topological correlation; the LLM is strictly an explanation layer, never the source of truth or decision maker.
4. **Local-First & Budget-Conscious**: Local development via Docker Compose is the primary environment. Azure deployment targets remain candidate options evaluated against a strict ~$5–10/month budget envelope with no cloud resources provisioned prematurely.

---

## Documentation Structure

All foundational architectural decisions, guidelines, and specifications are cataloged in `docs/`:

* [`docs/architecture/overview.md`](docs/architecture/overview.md): High-level system architecture, refined 4-pillar domain models, module boundaries, and Mermaid diagrams.
* [`docs/adr/`](docs/adr/): Architecture Decision Records (ADRs) capturing problem context, alternatives, decisions, and consequences.
  * [`docs/adr/template.md`](docs/adr/template.md): Template for future ADRs.
  * [`docs/adr/0001-record-architecture-decisions.md`](docs/adr/0001-record-architecture-decisions.md): Decision to use ADRs.
  * [`docs/adr/0002-modular-monolith-clean-hexagonal-architecture.md`](docs/adr/0002-modular-monolith-clean-hexagonal-architecture.md): Architectural pattern rationale.
  * [`docs/adr/0003-core-technology-stack.md`](docs/adr/0003-core-technology-stack.md): Technology evaluation and justifications.
* [`docs/api/`](docs/api/): API design standards, versioning, error schemas, and contracts.
* [`docs/operations/azure-cost-and-infra.md`](docs/operations/azure-cost-and-infra.md): Cost drivers, budget controls, telemetry limits, and candidate cloud deployment models.
* [`docs/development/standards.md`](docs/development/standards.md): Code quality rules, typing, async patterns, logging, and testing philosophy.
* [`docs/development/environment.md`](docs/development/environment.md): Local developer setup and CI/CD pipeline design.
* [`AGENTS.md`](AGENTS.md): Strict architectural guardrails and anti-debt rules for AI coding assistants.

---

## Quickstart (Local Backend)

1. Start PostgreSQL:
   ```bash
   docker compose up -d postgres
   ```
2. Set up virtual environment and install dependencies:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Run tests and static analysis:
   ```bash
   pytest -v
   ruff check .
   ruff format --check .
   mypy src tests
   ```
5. Start the backend API:
   ```bash
   python src/traceops/main.py
   # Health check: http://localhost:8001/api/v1/health
   # Readiness check: http://localhost:8001/api/v1/ready
   ```

---

## Current Status

**Phase 1A: Backend Engineering Foundation Complete.**  
Runnable modular monolith foundation with FastAPI, clean architecture boundaries, async PostgreSQL session management, Alembic migrations, RFC 7807 error handling, structured logging with correlation IDs, and unit/integration testing suite. No domain entities, database tables, or product logic have been implemented.
