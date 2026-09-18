# NestJS Backend Verification & Quality Checklist

Comprehensive checklist for reviewing NestJS backend pull requests, refactorings, and architecture changes.

---

## 1. Architecture & Dependency Injection Audit

- [ ] **Feature-First Organization:** Modules grouped by domain capability (`OrdersModule`, `UsersModule`) rather than technical type (`ControllersModule`, `ServicesModule`).
- [ ] **Thin Controllers (< 150 lines):** Controllers only handle HTTP binding, parameter extraction, and status codes; zero inline SQL, Prisma queries, or business calculations.
- [ ] **Stateless Singletons:** Services do not store request-specific state in instance properties.
- [ ] **No Circular Dependencies:** Feature modules are free of circular imports; no unverified `forwardRef()` workarounds.
- [ ] **Constructor Injection:** All dependencies injected via class constructors using `private readonly`; no property injection (`@Inject()` on properties).
- [ ] **Repository Abstraction:** Direct database client access (Prisma / TypeORM / Knex) abstracted behind repository interfaces or data access modules.

---

## 2. Security Audit

- [ ] **Global Validation Pipe Enabled:** `ValidationPipe` configured with `whitelist: true`, `forbidNonWhitelisted: true`, and `transform: true`.
- [ ] **Strict DTO Binding:** Every endpoint receiving `@Body()`, `@Query()`, or `@Param()` binds to an explicit typed DTO with validation decorators.
- [ ] **Object-Level Authorization (BOLA/IDOR):** Endpoints accessing tenant or user data verify ownership against `req.user.id` or `tenantId`.
- [ ] **Guards on Protected Routes:** All non-public endpoints protected by `@UseGuards(JwtAuthGuard, RolesGuard)` or global guards with `@Public()` decorators.
- [ ] **Output Sanitization:** Sensitive fields (`passwordHash`, `refreshToken`, internal secrets) excluded via `ClassSerializerInterceptor` (`@Exclude()`) or explicit response mapping.
- [ ] **Rate Limiting:** Public endpoints (auth, password reset, webhooks) protected with `@nestjs/throttler`.

---

## 3. Database & Performance Audit

- [ ] **Atomic Multi-Step Mutations:** Operations touching multiple database rows wrapped in a transaction (`prisma.$transaction()` or TypeORM `QueryRunner`).
- [ ] **N+1 Query Prevention:** Entity relations fetched with eager joins, batch queries, or DataLoaders rather than mapping queries inside loops.
- [ ] **Database Index Coverage:** Foreign keys and columns queried in `WHERE` clauses backed by explicit database indexes.
- [ ] **Connection Pool Sizing:** Database client configured with explicit connection limits and idle timeouts.
- [ ] **Caching Layer:** Frequently read, rarely changed data cached in Redis or in-memory cache with explicit TTL.

---

## 4. Error Handling & Resilience Audit

- [ ] **Centralized Exception Filters:** Application registers global exception filters mapping unhandled exceptions to structured JSON responses.
- [ ] **Semantic HTTP Exceptions:** Services throw standard NestJS HTTP exceptions (`NotFoundException`, `ConflictException`, `BadRequestException`) rather than generic `Error` instances.
- [ ] **Async Error Safety:** All promises properly awaited or returned; zero unhandled promise rejections.

---

## 5. Testing & Verification Audit

- [ ] **Supertest E2E Coverage:** Critical API user journeys exercised with Supertest against running NestJS application.
- [ ] **Observable Behavior Assertions:** Tests assert HTTP status codes, headers, and response payloads rather than verifying internal mock call counts.
- [ ] **Doctor Checks Passed:** Database connection, Redis liveness, and pending migrations verified before running test suite.
- [ ] **Zero Test Residue:** Test database tables truncated and open connections cleanly closed (`await app.close()`) post-test.
- [ ] **The Undefined Check:** Tests verified to ensure they would fail if imported service methods returned `undefined`.

---

## 6. TypeScript Discipline Audit

- [ ] **Zero `as any`:** External data typed as `unknown`; casts permitted only after schema validation.
- [ ] **Branded Entity IDs:** Identifiers (`UserId`, `OrderId`, `TenantId`) branded to eliminate cross-assignment bugs.
- [ ] **Discriminated Unions:** API response envelopes, worker jobs, and domain events modeled with literal status discriminants.
- [ ] **Types as Constructions:** Types built up from valid components; impossible domain states made unrepresentable.
- [ ] **Compile-Time Exhaustiveness:** Switch statements over domain sum types feature an inline `const _exhaustive: never = state;` default arm.

---

## 7. Code Documentation Integrity Audit

- [ ] **Zero Meaningless Comments:** No comments narrating trivial code (`// constructor`, `// inject service`, `// find by id`).
- [ ] **Zero Dead Commented-Out Code:** No commented-out legacy code blocks committed.
- [ ] **High-Signal "WHY" Explanations:** Comments solely document non-obvious business logic, database locking strategies, or performance tradeoffs.
- [ ] **Strict Freshness:** All comments accurately reflect the latest implementation.

---

## 8. Unslop Writing Audit

- [ ] **Zero AI Buzzwords:** Documentation and comments avoid buzzwords ("crucial", "pivotal", "delve", "foster", "testament", "tapestry", "landscape", "enhance").
- [ ] **Concrete Numbers Over Metaphor:** Concrete figures stated directly instead of emotional impressions ("handles 1,500 req/s with 15ms p95").
- [ ] **Clean Typography:** Zero decorative emojis in code headings; periods or commas used instead of em dashes.
- [ ] **Active Voice:** Sentences use active voice with named actors.

---

## 9. Foundational Engineering Principles Audit

- [ ] **Root-Cause Fixes:** Bugs resolved at the root origin rather than masked with downstream optional chaining (`?.`) or silent null guards.
- [ ] **Data Structures Precede Logic:** Database entities, domain schemas, and DTOs finalized before route logic.
- [ ] **Subtract Before Adding:** Dead endpoints, unused service methods, and legacy DTOs removed prior to introducing new features.
- [ ] **Prove It Works:** Endpoints verified by executing actual HTTP requests or deterministic verification scripts.
- [ ] **Laziness Protocol:** Call hierarchies kept flat (< 3 layers); branching consolidated into guards/registries.
- [ ] **Attack the Premise:** Repeated concurrency/deadlock failures investigated by questioning shared assumptions.
- [ ] **Minimize Reader Load:** Pass-through wrappers collapsed; services kept stateless; 30-second trace test passes.
- [ ] **Model the Domain:** Domain invariants encoded in data structures; zero synchronized database booleans.
- [ ] **Never Block on the Human:** Autonomous momentum maintained on reversible backend refactorings.
- [ ] **Outcome-Oriented Migrations:** Direct convergence on target architecture without temporary throwaway shims.
- [ ] **First-Principles Integration:** New requirements architected holistically from the ground up across migrations, entities, and DTOs.
- [ ] **Verifiable Unit Sequencing:** Work decomposed into atomic, verifiable brackets (red-to-green per unit).
- [ ] **Migrate Callers & Delete Legacy APIs:** Deprecated internal service methods or endpoints removed alongside caller migration; zero dual-path legacy shims.
