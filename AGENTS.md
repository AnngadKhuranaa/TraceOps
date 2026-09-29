# TraceOps AI Coding Guardrails

This document establishes non-negotiable rules for any AI assistant or automated agent contributing code to the TraceOps repository. Violations of these rules represent architectural regressions and must be rejected.

---

## 1. Architectural Integrity & Strict Dependency Boundaries

The source-code dependency direction is strictly:
```
Presentation ──► Application ──► Domain
```
Infrastructure exists strictly outside the inner layers and implements ports/interfaces defined by Application and Domain boundaries.

1. **Zero External Framework Dependencies in Domain**:
   - The `domain/` layer must contain pure Python dataclasses, entities, value objects, and domain exceptions.
   - **FORBIDDEN** in `domain/`:
     - FastAPI or any HTTP transport library
     - SQLAlchemy, SQLModel, ORMs, or database drivers
     - Pydantic (prefer standard Python dataclasses for domain purity; avoid Pydantic in domain models)
     - Azure SDKs, AWS SDKs, GCP SDKs
     - GitHub SDKs or client libraries
     - OpenAI, LangChain, or LLM SDKs
     - Direct infrastructure modules or third-party I/O packages
2. **Strict Inward Dependency Flow**:
   - `Presentation` depends on `Application`.
   - `Application` depends on `Domain` and defines Port interfaces (abstract base classes / protocols).
   - `Infrastructure` implements Application and Domain Ports.
   - **FORBIDDEN**: `Application` importing concrete infrastructure adapters.
   - **FORBIDDEN**: `Domain` importing any outer layer (`Application`, `Infrastructure`, `Presentation`).
3. **No Business Logic in Presentation**:
   - FastAPI routers must strictly handle HTTP request parsing, authentication context passing, invoking an Application Use Case, and mapping results to HTTP response models.
   - **FORBIDDEN**: Business rules, calculations, scoring, filtering logic, or direct persistence/database queries inside route handlers.
4. **Focused Infrastructure Adapters (Anti-Dumping Ground Rules)**:
   - Adapters must have one clear, focused responsibility.
   - Adapters must implement one or more explicit Application Ports.
   - Adapters must isolate external providers (e.g. Azure Activity Logs adapter, GitHub Events adapter).
   - **FORBIDDEN**: Adapters containing domain decision logic or scoring algorithms.
   - **FORBIDDEN**: Adapters performing unrelated orchestration across disparate systems.
   - **FORBIDDEN**: "God classes" or "god modules" that bundle unrelated cloud or persistence capabilities.
   - **FORBIDDEN**: Cloud adapters directly calling unrelated external systems.
   - **FORBIDDEN**: Direct cloud SDK usage outside designated infrastructure adapters.

---

## 2. Domain Model Integrity: Facts vs Hypotheses vs Evidence vs Explanations

All causal analysis code must respect the strict conceptual separation:
1. **Facts**: Immutable observations about what actually occurred (e.g., deployment executed, config changed, metric anomaly detected). Facts are collected, never manufactured.
2. **Hypotheses**: Candidate explanations for an incident (e.g., "Deployment X caused incident Y"). Generated systematically from candidates.
3. **Evidence**: Observable facts and calculated metrics supporting or weakening a hypothesis (e.g., temporal proximity, topological path distance, anomaly correlation, change blast radius).
4. **Explanations**: Human-readable narrative synthesized strictly from verified evidence.
   - **FORBIDDEN**: Allowing an LLM to decide the root cause, assign scores, or invent hypotheses without deterministic backing.
   - The Root Cause Engine must strictly follow:  
     `Evidence` ➔ `Candidate generation` ➔ `Candidate scoring` ➔ `Ranking` ➔ `Evidence graph` ➔ `Optional LLM explanation`.

---

## 3. Anti-Debt Guardrails & Simplicity (Do Not Over-Architect)

This codebase is built by a solo developer. Every change must remain within the smallest reasonable architectural boundary.

1. **FORBIDDEN Premature Architectural Complexity**:
   - **NO** microservices or distributed service mesh.
   - **NO** external message brokers (Kafka, RabbitMQ, Azure Service Bus).
   - **NO** distributed background task workers (Celery, Dramatiq) or caching layers (Redis) unless measured requirements justify them.
   - **NO** Kubernetes or complex container orchestration.
   - **NO** complex Event Sourcing or CQRS frameworks.
   - **NO** specialized time-series engines (TimescaleDB) or dedicated graph databases until data volume proves PostgreSQL inadequate.
   - **NO** premature machine learning models (GBDT, neural nets) before deterministic scoring is exhaustively validated.
2. **No Duplicate or Speculative Abstractions**:
   - Do not create generic base classes, wrapper utilities, or abstractions without at least two real call sites.
   - Do not create placeholder methods ("for future extension"), dead interfaces, or uncalled configuration flags.
3. **Scope Discipline**:
   - Only modify files directly relevant to the current task. Do not reformat unrelated files or touch other module contracts without explicit architectural review.
   - Avoid circular dependencies; maintain clear one-way module dependencies.

---

## 4. Code Quality, Typing & Error Handling

1. **Strict Type Annotations**:
   - All function and method signatures must include explicit parameter and return type annotations.
   - **FORBIDDEN**: Using `Any` as a shortcut to bypass type checking. Use `TypeVar`, generics, or explicit Protocols.
   - **FORBIDDEN**: Disabling `mypy` or `pyright` comments (`# type: ignore`) unless accompanied by an explanatory comment detailing a verified third-party typing bug.
2. **Error Handling & Exceptions**:
   - **FORBIDDEN**: Naked `except:` or catching broad `except Exception:` without logging and re-raising or wrapping in a domain-specific exception.
   - Domain logic must raise domain-specific exceptions (e.g., `IncidentNotFoundError`, `InvalidTimeWindowError`).
   - Presentation/Application layers map domain exceptions to RFC 7807 HTTP status codes.
3. **Structured Logging**:
   - Use structured logging (key-value attributes) with correlation IDs (`incident_id`, `trace_id`).
   - Do not log sensitive credentials, authorization tokens, or raw unredacted customer payloads.

---

## 5. Testing Discipline

1. **Deterministic Domain Testing**:
   - Domain unit tests must execute in-memory with zero I/O, zero network calls, zero database connections, and zero live cloud dependencies.
   - **FORBIDDEN**: Requiring real Azure credentials or network access for unit tests.
   - Root-cause scoring must be tested deterministically with synthetic incidents that possess predetermined, verifiable ground truths.
2. **Adapter Testing**:
   - External integrations and cloud adapters must be tested separately using test doubles, recorded responses, or isolated integration tests.
3. **Test Integrity**:
   - **FORBIDDEN**: Weakening or skipping tests to make CI pass.
   - **FORBIDDEN**: Disabling static analysis, linting, or type checking in CI.

---

## 6. Pre-Task Checklist for AI Agents

Before submitting code, verify:
- [ ] Did I place business logic in the domain or application layer rather than FastAPI routes?
- [ ] Does my domain code import any infrastructure, ORM, Pydantic, or third-party SDKs?
- [ ] Are all adapters focused on a single responsibility and implementing explicit ports?
- [ ] Does the root cause logic keep the LLM strictly as an explanation layer and not a decision maker?
- [ ] Did I avoid adding unnecessary distributed tools (Kafka, Redis, Celery, TimescaleDB)?
- [ ] Are all types strictly specified without unneeded `Any`?
- [ ] Are exceptions handled explicitly with domain-specific exceptions?
- [ ] Can all unit tests run completely offline without cloud credentials?
