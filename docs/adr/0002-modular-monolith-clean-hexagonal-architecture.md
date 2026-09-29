# ADR 0002: Modular Monolith with Clean & Hexagonal Architecture

* **Status**: Accepted
* **Date**: 2026-09-29
* **Author**: Principal Software Architect
* **Deciders**: TraceOps Engineering

---

## 1. Context and Problem Statement

TraceOps is an incident investigation and root-cause intelligence platform targeting Azure initially, with plans for AWS/GCP extensibility. The project is developed by a single engineer. Building a distributed microservices architecture introduces extreme operational complexity (distributed tracing, network serialization, saga patterns, multiple deployment pipelines, local orchestration overhead). Conversely, an unstructured monolith leads to tight coupling, leaky cloud dependencies, and unmaintainable code.

---

## 2. Decision Drivers

* **Single-developer ergonomics**: Low cognitive and operational overhead; avoiding premature distributed systems.
* **Strict domain isolation**: Domain logic must remain 100% pure Python without dependencies on Azure SDKs, PostgreSQL, FastAPI, Pydantic, or LLMs.
* **Deterministic testability**: Pure business logic and causal scoring must be testable in sub-second unit tests without live services or external mocks.
* **Focused adapters**: Preventing the infrastructure layer from becoming a dumping ground or collection of "god classes".
* **Future extraction pathway**: Ability to spin off high-throughput ingestion or detection as standalone services later if load demands it, without rewriting business logic.

---

## 3. Considered Alternatives

### Alternative 1: Microservices Architecture
* **Pros**: Independent deployability, independent scaling.
* **Cons**: Severe operational complexity, high local development friction, distributed failure modes, premature optimization for a solo developer.

### Alternative 2: Traditional Layered Monolith (CRUD / MVC)
* **Pros**: Simple to set up initially.
* **Cons**: High risk of database and framework bleed into business rules; tightly couples business logic to ORM/database schemas; hard to test without database.

### Alternative 3: Modular Monolith with Clean & Hexagonal Architecture (Ports and Adapters)
* **Pros**: Single deployment unit and single codebase; strict boundaries enforced via in-process module interfaces; inner domain is pure Python; infrastructure connects via ports; highly testable; easy to extract into services later.
* **Cons**: Requires initial discipline with interfaces and mapping models between layers.

---

## 4. Decision

We choose **Modular Monolith with Clean and Hexagonal Architecture (Ports and Adapters)**.

### Architectural Rules:
1. **Strict Dependency Direction**:
   - `Presentation` ➔ `Application` ➔ `Domain`.
   - `Infrastructure` implements `Application` and `Domain` ports.
   - `Domain` MUST NOT import `FastAPI`, `SQLAlchemy`, `Pydantic`, `Azure SDKs`, `GitHub SDKs`, `OpenAI SDKs`, or infrastructure modules.
   - `Application` MUST NOT import concrete infrastructure adapters.
   - `Presentation` MUST NOT contain business logic or direct persistence queries.
2. **Four Domain Pillars**:
   - **Facts**: Immutable observations about what happened (deployments, config changes, metric values).
   - **Hypotheses**: Candidate root cause explanations.
   - **Evidence**: Observable facts and metrics supporting or weakening a hypothesis.
   - **Explanation**: Human-readable synthesis of verified evidence (LLM is an explanation layer, never a decision maker).
3. **Focused Infrastructure Adapters**:
   - Every adapter must have one single responsibility, implement explicit ports, and contain zero scoring or domain logic.
4. **Anti-Over-Architecting Discipline**:
   - No Kafka, RabbitMQ, Redis, Celery, Kubernetes, service mesh, distributed microservices, complex event sourcing, CQRS, TimescaleDB, or graph databases unless later measured requirements justify them.

---

## 5. Consequences & Implications

* **Positive**: Fast local iteration, simple single-container deployment, deterministic unit tests without network calls, clean cloud-agnostic domain.
* **Negative**: Requires strict enforcement to prevent architectural regressions. Enforced via `AGENTS.md` and CI checks.
