# TraceOps Engineering Standards & Coding Guidelines

## 1. Naming & Module Conventions

* **Modules and Packages**: `snake_case` (e.g., `incident_repository.py`, `candidate_scoring/`).
* **Classes and Protocols**: `PascalCase` (e.g., `ChangeEventRepository`, `TopologyGraph`).
* **Functions and Methods**: `snake_case` (e.g., `calculate_topological_distance()`).
* **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_LOOKBACK_MINUTES`).
* **Port Interfaces**: Name ports by their capability or role (e.g., `IncidentRepositoryPort`, `TelemetryCollectorPort`, `ExplanationGeneratorPort`).

---

## 2. Enforceable Dependency Direction & Boundary Rules

Source-code dependency direction is strictly:
```
Presentation ──► Application ──► Domain
```
Infrastructure exists strictly outside the inner layers and implements ports/interfaces defined by Application and Domain boundaries.

### 2.1 Domain Layer Rules
* The domain layer contains pure Python dataclasses, entities, value objects, and domain exceptions.
* **FORBIDDEN IMPORTS in `domain/`**:
  * FastAPI or any HTTP routing library
  * SQLAlchemy, SQLModel, database drivers, or ORMs
  * Pydantic (prefer standard Python dataclasses for domain purity)
  * Azure SDKs, AWS SDKs, GCP SDKs
  * GitHub SDKs or client libraries
  * OpenAI, LangChain, or LLM SDKs
  * Infrastructure modules or concrete adapters

### 2.2 Application Layer Rules
* Contains orchestrating use cases and defines abstract Port interfaces (protocols).
* **FORBIDDEN IMPORTS in `application/`**: Concrete infrastructure adapters.

### 2.3 Presentation Layer Rules
* Handles HTTP request parsing, authentication context passing, invoking application use cases, and serializing responses.
* **FORBIDDEN in `presentation/`**: Business logic, causal scoring, candidate ranking, or direct database/persistence queries.

### 2.4 Infrastructure Adapter Rules (Anti-Dumping Ground)
To prevent the infrastructure layer from becoming an unmaintainable dumping ground:
* **Single Responsibility**: Each adapter must isolate one specific external provider or persistence mechanism (e.g., `AzureActivityLogAdapter`, `GitHubEventsAdapter`, `PostgresIncidentRepository`).
* **Explicit Port Implementation**: Every adapter must implement one or more explicitly defined application ports.
* **No Domain Decision Logic**: Adapters must never contain scoring algorithms, business rules, or candidate ranking heuristics.
* **No Unrelated Orchestration**: Adapters must not coordinate workflows across disparate external systems; orchestration belongs in application use cases.
* **No "God Classes"**: Adapters must remain small and focused; avoid monolithic classes wrapping multiple cloud services.
* **No Cross-Calling**: Adapters must not directly invoke other unrelated external APIs or adapters.
* **SDK Confinement**: Direct cloud SDK usage is strictly quarantined inside designated infrastructure adapters.

---

## 3. Domain Model Pillars: Facts, Hypotheses, Evidence, and Explanations

All causal analysis code must respect the conceptual separation:
1. **Facts**: Immutable observations about what actually happened (e.g., deployment occurred, config changed, metric anomaly detected). Facts are collected, never manufactured.
2. **Hypotheses**: Candidate explanations for an incident (e.g., "Deployment X caused incident Y").
3. **Evidence**: Observable facts and deterministic metrics supporting or weakening a hypothesis (temporal proximity, dependency graph distance, anomaly correlation, blast radius).
4. **Explanations**: Human-readable narrative synthesized strictly from verified evidence.
   - The Root Cause Engine must strictly follow:  
     `Evidence` ➔ `Candidate generation` ➔ `Candidate scoring` ➔ `Ranking` ➔ `Evidence graph` ➔ `Optional LLM explanation`.
   - The LLM is an explanation layer, **never the source of truth or decision maker**.

---

## 4. Strict Type Annotations

* Every function and method signature must have explicit parameter and return type annotations.
* **FORBIDDEN**: Using `Any` as a shortcut. Use generics (`TypeVar`), `Union`, or explicit Protocols.
* **FORBIDDEN**: Suppressing type checker errors (`# type: ignore`) unless accompanied by an explanatory comment detailing a verified third-party typing bug.
* Enforced via `mypy --strict`.

---

## 5. Error Handling & Domain Exceptions

* Define domain-specific exceptions inheriting from a base `TraceOpsError`:
  ```python
  class TraceOpsError(Exception):
      """Base exception for all domain errors in TraceOps."""

  class IncidentNotFoundError(TraceOpsError):
      def __init__(self, incident_id: str) -> None:
          super().__init__(f"Incident '{incident_id}' not found.")
          self.incident_id = incident_id
  ```
* **FORBIDDEN**: Naked `except:` or catching broad `except Exception:` without logging and re-raising or wrapping in a domain-specific exception.
* Presentation layer maps domain exceptions to RFC 7807 Problem Details HTTP responses.

---

## 6. Structured Logging

* Use structured logging emitting JSON logs with key-value pairs.
* Every log line must include correlation identifiers (`correlation_id`, `incident_id`).
* Never log raw credentials, authorization tokens, connection strings, or customer PII.

---

## 7. Testability Architecture

1. **Domain Unit Tests (`tests/unit/`)**:
   - Must be 100% deterministic, executing in sub-seconds.
   - Zero I/O, zero network calls, zero database connections, zero cloud credentials required.
2. **Deterministic Root-Cause Scoring**:
   - Candidate ranking and scoring algorithms must be verified against synthetic incident fixtures (`tests/fixtures/synthetic_incidents/`) with predetermined, known ground truths.
3. **Integration Tests (`tests/integration/`)**:
   - External cloud adapters and database repositories must be tested separately using test doubles, recorded mocks (VCR), or local ephemeral test containers.

---

## 8. Anti-Over-Architecting Discipline (Solo-Developer Scale)

To preserve long-term maintainability for a solo developer, the following technologies are **FORBIDDEN** unless a later, measured requirement justifies them:
* Kafka, RabbitMQ, or Azure Service Bus
* Celery, Dramatiq, or Redis caching
* Kubernetes or service meshes
* Distributed microservices
* Complex Event Sourcing or CQRS frameworks
* TimescaleDB or dedicated graph databases
* Machine learning ranking models before deterministic scoring is fully validated
