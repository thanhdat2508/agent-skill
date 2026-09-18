# Foundational Engineering Principles for NestJS Backend Architecture

Core engineering principles governing root-cause problem solving, architectural planning, type safety, and AI pairing for NestJS backend engineers.

---

## 1. Fix Root Causes, Not Symptoms

When debugging backend exceptions, database timeouts, memory leaks, or unhandled promise rejections:
- **Trace to the root origin:** Fix the failure at its architectural or data source rather than catching and swallowing errors downstream.
- **Resist defensive nil-check patches:** Adding a `?.` or fallback default in a service often masks a missing database relation, a failing foreign key cascade, or a malformed upstream DTO. Fix the database query or the controller validation pipe instead.
- **Reproduce before patching:** Write an isolated unit test or Supertest E2E test reproducing the exact input payload and edge case before touching implementation code.
- **Check for the pattern:** When a defect is discovered (such as a missing database transaction or an unindexed query), grep across the codebase to fix all occurrences across all feature modules.
- **Suspect state before code on restart bugs:** If an issue occurs on server reboot or worker restart, audit persistent external state first (Redis locks, database connection pool exhaustion, stale migration status, or uncommitted transactions).

---

## 2. Foundational Thinking: Data Structures and Scaffolding First

- **Data structures precede service logic:** Model database entities, DTOs, domain aggregate roots, and event schemas before writing controller routes or business logic. When data models match the dominant query and access patterns, service code remains clean and declarative.
- **Subtraction before scaffolding:** Remove deprecated endpoints, unused service methods, and dead modules before laying new architecture.
- **Scaffold before features:** Establish database migrations, DTO validation pipes, exception filters, repository interfaces, and test fixtures before implementing feature logic.
- **Concurrency and shared state isolation:** Before sharing state across requests, verify thread safety and request isolation. Remember that NestJS services are singletons by default; never store per-request state in service instance fields.
- **Avoid premature abstractions:** Three similar lines in two separate services beat a premature, leaky generic base service. Abstract only when boundaries and domain reuse are fully validated.

---

## 3. Guard the Context Window

Context tokens are finite and non-renewable within an AI agent pairing session:
- **Isolate large payloads:** When running database migrations, Docker builds, or large E2E test suites, extract high-level summaries and failure traces rather than dumping megabytes of raw logs into context.
- **Read selectively:** Read specific method line ranges rather than loading entire multi-thousand line entity or service files.
- **Cap scope per phase:** Complete modular backend refactorings sequentially module by module (e.g. `AuthModule` -> `UsersModule` -> `BillingModule`).

---

## 4. Prove It Works

Verify every backend change by exercising the real artifact directly:
- **Never infer from proxies:** Do not trust "it builds without TypeScript errors" or green linter checks alone. Exercise the actual HTTP endpoint, message queue handler, or database transaction.
- **Verify full data path:** Trace data from the HTTP request body through the Guard, Pipe, Controller, Service, Repository, down to the database row and back to the serialized response.
- **Script deterministic verification:** Write deterministic verification scripts (Supertest suites, curl-based bash scripts, or database verification scripts) that reviewers can execute repeatedly.
- **Inspect actual diffs:** When delegating tasks to subagents, review the real git diff, database migration files, and test outputs rather than trusting verbal summaries.

---

## 5. Test Behavior, Not Implementation

A test calls the backend API the way clients do and asserts observable responses against literal expected values:
- **The Undefined Check:** Before keeping a test, ask if it would still pass if every imported dependency returned `undefined`. If yes, the test observes no real behavior. Rewrite or delete it.
- **Ban mock-only assertions:** Avoid tests that only assert `expect(service.find).toHaveBeenCalled()`. Assert the actual return value, HTTP status code, or state change in the test database.
- **Ban constant pinning:** Do not assert against hardcoded configuration defaults or internal constant definitions (`expect(JWT_EXPIRATION).toBe('1h')`). Test the authentication mechanism that verifies expired tokens.
- **Assert literal values:** Call services and endpoints with concrete payloads and assert literal responses (`expect(res.body.data.amount).toBe(1500)`).
- **Prefer Supertest E2E tests:** For critical user journeys, run Supertest against the running NestJS application with a test database container rather than mocking every layer.

---

## 6. Laziness Protocol

Maximize backend throughput and reliability while minimizing code volume:
- **Bias toward deletion:** When refactoring existing modules, seek removals before additions.
- **Maintain a flat call hierarchy:** Keep call depth under 3 layers: `Controller -> Service -> Repository`. Avoid creating intermediate manager, helper, coordinator, and adapter wrappers that only forward arguments.
- **Consolidate decisions:** Consolidate business rules and authorization policies into dedicated Guards or domain services rather than scattering checks across controllers.
- **Minimize the diff:** Make the smallest change that solves the root problem. Clean minimal code beats complex architectural boilerplate.
- **Question signal threading:** Avoid passing flags or configuration parameters through 4 layers of service constructors when dependency injection or async storage provides direct access.

---

## 7. Attack the Premise

When two or more attempted fixes fail to resolve an issue (e.g. database deadlocks, race conditions, or connection pool exhaustion):
- **Write down the shared premise:** Explicitly state the assumption common to all failed attempts (e.g., "we assumed requests must be processed synchronously in order").
- **Census actor imbalance:** Measure which endpoints, database tables, or background queues experience the deadlock or contention.
- **Analyze skew:** Determine what architectural mechanism assigns that load or lock to those specific actors.
- **Eliminate structural asymmetry:** Replace the bottleneck mechanism (e.g., switch from synchronous database locking to an idempotent background queue or optimistic concurrency with version columns) rather than adding complex retry loops.
- **Stop before retrying:** Never launch a third workaround that assumes the same invalidated premise.

---

## 8. Minimize Reader Load

Maintainability is the work an engineer must do to understand backend code:
- **Layers to trace:** Keep indirections under 3 levels between an API endpoint and the underlying database operation.
- **State to hold:** Keep NestJS services strictly stateless; favor pure domain functions with returned values over mutating object properties.
- **Demand interface compression:** Ensure each layer meaningfully transforms data (e.g., DTO to domain model, domain model to database row) rather than creating pass-through stubs.
- **The 30-Second Rule:** A new backend engineer must be able to answer "where does this API response come from?" and "what can mutate this database column?" in under 30 seconds.

---

## 9. Model the Domain in Data Structures

Encode business rules and domain invariants directly into data structures:
- **Make invalid states unrepresentable:** Use TypeScript discriminated unions, state machines, and aggregate roots rather than loose bags of optional fields.
- **Ban synchronized database booleans:** Never introduce two database columns that must stay synchronized (e.g., `isCancelled: boolean` and `cancelledAt: Date`). Store `cancelledAt: Date | null` and derive `isCancelled` via a domain getter.
- **Eliminate branching with registries:** Use handler maps or strategy patterns instead of cascading `switch` statements across multiple services.
- **Organize by domain boundaries:** Group modules by domain capability (`OrdersModule`, `PaymentsModule`) rather than technical phases (`LoadersModule`, `ValidatorsModule`).

---

## 10. Never Block on the Human (Proceed, Then Present)

Human supervision is asynchronous; agents must maintain forward momentum on reversible backend engineering:
- **Proceed, then present:** Execute reversible tasks (generating DTOs, implementing services, writing repository methods, creating unit tests), present the verified outcome, and let the engineer course-correct asynchronously.
- **Don't ask permission on reversible work:** Avoid pausing execution to ask "Should I create a DTO?". Create the DTO, state why, and provide the diff.
- **Reserve questions for genuine ambiguity:** Solicit user input only when business requirements or domain logic cannot be inferred from repository context.
- **Hard boundaries on irreversible actions:** Always request confirmation before irreversible actions (dropping database tables, running production migrations, force-pushing branches, deleting seed data).

---

## 11. Outcome-Oriented Execution (Target Architecture Over Transitional Debt)

During planned backend rewrites, ORM migrations (e.g., TypeORM to Prisma), or architectural refactors:
- **Target state integrity:** Prioritize the final verified end state over preserving transitional backward compatibility.
- **Reject throwaway compatibility layers:** Avoid creating complex translation layers that exist solely to smooth intermediate steps; they turn into long-term technical debt.
- **Accept planned, scoped intermediate breakage:** Isolate intermediate refactoring steps within a dedicated branch or phase, then run comprehensive verification upon completion.

---

## 12. Redesign from First Principles

When integrating a major new backend requirement into an existing service:
- **Foundational question:** Ask: "If this requirement had existed from day one, how would we have designed this database schema, entity model, and service hierarchy?"
- **Holistic propagation:** Update the entire stack: database migrations, entities, repositories, DTOs, services, controllers, exception filters, and test suites.
- **Preserve option value:** Design the complete coherent architecture upfront, then deliver it in clean, incremental PRs.

---

## 13. Sequence Work into Verifiable Units

Decompose complex backend tasks, migrations, and refactorings into small, verifiable brackets:
- **Red-to-green incrementality:** Never advance to step N+1 while step N is failing. Localize failures immediately at the unit that caused them.
- **Before/after bracket:** Frame each step as a clear bracket: known-good baseline, single atomic change, verify passing state, then advance.
- **Stack for proof:** Order commits logically (e.g., failing Supertest first, then database migration, then repository update, then service implementation).

---

## 14. Subtract Before You Add

When evolving a backend system, remove dead code and complexity before building new features:
- **Sequence removal before construction:** Delete deprecated endpoints, unused service methods, and legacy DTOs before adding new capabilities.
- **Cut before you polish:** Strip the implementation down to its essential domain model before investing in caching or microservice optimization.
- **Design for observed usage:** Avoid building speculative pagination filters, theoretical bulk-mutation endpoints, or unused event handlers beyond specification requirements.

---

## 15. Type-System Discipline (The Compiler as Proof Assistant)

Treat TypeScript as a formal compile-time proof assistant:
- **Make illegal states unrepresentable:** Model domain variants as discriminated unions (`type Payment = { status: 'pending' } | { status: 'completed'; transactionId: string }`).
- **Brand semantic primitives:** Ensure `UserId`, `OrderId`, and `TenantId` are branded types rather than interchangeable strings.
- **Parse at boundaries:** Validate every incoming HTTP payload with DTOs using `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })` or Zod schemas.
- **Never lie to the compiler:** Prohibit `as any` and unearned type assertions. Validate external webhook payloads before casting.
- **Enforce exhaustiveness:** Verify every union match with `const _exhaustive: never = state;` so adding a new domain state triggers compile errors.
- **Total functions in services:** Push partiality checks into types to eliminate unexpected runtime exceptions.

---

## 16. Migrate Callers Then Delete Legacy APIs

When replacing an internal service method, repository query, or DTO:
- **Migrate and delete in the same wave:** Inventory all existing call sites, refactor them to the new API, and immediately delete the legacy implementation in the same atomic change.
- **Reject permanent compatibility shims:** Avoid keeping deprecated methods or alias endpoints alive solely because internal callers exist. Dual-path architectures confuse developers and AI agents.
- **Eliminate append-only drift:** Treat internal backend codebases as living systems, not append-only logs.
- **Update test contracts:** Rewrite test suites to assert the behavior of the new API, deleting tests that only guarded legacy implementation details.

---

## 17. Adversarial Review & Interrogation

Before shipping high-impact backend changes (database migrations, authentication guards, payment services):
- **Independent multi-model review:** Challenge diffs against an objective rubric covering Security (OWASP, IDOR, SQLi), Data Integrity (transactions, race conditions, N+1), and Architecture.
- **Synthesize consensus:** Prioritize issues surfaced by multiple models independently.
- **Pragmatic lead judgment:** Classify findings into **Act On** (critical security/data integrity blockers), **Consider** (tradeoffs), **Noted** (context-dependent), and **Dismissed** (invalid/nitpicky). Never auto-apply unverified feedback.

---

## 18. Maintain Verification Systems and Feature Maps

Keep backend verification harnesses, E2E tests, and feature documentation aligned with the running application:
- **Feature map hygiene:** Ensure documented API endpoints and RPC routes mirror active controllers and DTOs without documentation drift.
- **Doctor before driving:** Ensure database containers, Redis instances, and background workers pass health checks before running E2E test suites.
- **Clean test residue:** Truncate test database tables and flush test queues after test runs; never leave dangling processes or connections.
- **Explicit outcomes:** Report test and verification passes clearly as clean, changed, or blocked.
