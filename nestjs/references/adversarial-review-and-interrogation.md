# Adversarial Review & Interrogation for NestJS Backends

Multi-model adversarial review framework to challenge backend architecture, security boundaries, and database migrations.

---

## 1. When to Interrogate

Activate multi-model adversarial review for high-impact backend pull requests:
- New database schema migrations (especially column drops, renames, and foreign key index additions).
- Authentication, authorization guards, and permission interceptors.
- Financial transactions, billing flows, or checkout order services.
- Inter-service messaging, webhook listeners, or queue consumers.

---

## 2. Review Rubric for NestJS Backend Diffs

Every reviewer model evaluates the code diff against four core lenses:

### Lens A: Security & Access Control (OWASP API Top 10)
- **Broken Object-Level Authorization (BOLA/IDOR):** Does the service verify that the authenticated user (`req.user.id` or `tenantId`) owns the requested resource before mutating or reading?
- **Mass Assignment:** Does the controller use strict DTOs with `whitelist: true` and `forbidNonWhitelisted: true` to prevent callers from overwriting sensitive fields (e.g. `isAdmin: true`)?
- **Sensitive Data Exposure:** Are password hashes, API tokens, and internal IDs stripped from responses via `ClassSerializerInterceptor` or explicit DTO mapping?
- **Input Sanitization:** Are SQL/NoSQL queries parameterized to eliminate injection vulnerabilities?

### Lens B: Data Integrity, Transactions & Concurrency
- **Transaction Atomicity:** Do multi-step mutations execute inside an atomic database transaction (`prisma.$transaction()` or TypeORM `QueryRunner`)?
- **Race Conditions:** Are concurrent updates protected with optimistic locking (version column) or appropriate row-level locks?
- **N+1 Query Prevention:** Are relations loaded with eager joins or DataLoader/batching rather than mapping queries inside loops?

### Lens C: NestJS Architecture & DI Discipline
- **Singleton State Leaks:** Does any `@Injectable()` service store request-scoped data in instance fields?
- **Circular Dependencies:** Are modules free from circular imports and excessive `forwardRef()` workarounds?
- **Layer Violations:** Are controllers kept thin (< 100-150 lines) without direct ORM queries or raw business calculations?

### Lens D: Error Handling & Resilience
- **HTTP Exception Typing:** Does the service throw semantic NestJS HTTP exceptions (`NotFoundException`, `ConflictException`, `ForbiddenException`) instead of raw strings or unhandled runtime errors?
- **Async Handling:** Are all promises properly awaited or chained, preventing unhandled promise rejections?

---

## 3. Lead Judgment Framework

Synthesize findings from reviewer models and categorize every issue:

1. **Act On (Critical Blockers):**
   - Correctness, security vulnerabilities (IDOR, SQLi), data loss risks, or missing transaction boundaries.
   - Must be addressed before merging.

2. **Consider (Architectural Tradeoffs):**
   - Legitimate design suggestions (e.g. adding Redis caching, extracting a sub-service) where benefits must be weighed against implementation complexity.

3. **Noted (Context-Dependent):**
   - Valid observations that are not actionable in the current scope (e.g., future scaling optimizations).

4. **Dismissed (False Positives / Nits):**
   - Inaccurate findings or stylistic micro-preferences. Provide a one-sentence technical rationale explaining why the finding was dismissed.
