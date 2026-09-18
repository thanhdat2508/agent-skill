# NestJS Engineering Skill — Agent Routing Guide

> **AI Agent Notice:**
> To prevent context window bloat, do **not** read monolithic documentation upfront. Follow the **Progressive Disclosure** architecture:
> 1. Load [SKILL.md](./SKILL.md) for the 4-phase workflow and 7 core doctrines.
> 2. Load only the specific granular rule file(s) in [rules/](./rules/) matching your current task.
> 3. For the complete archival reference, see [docs/all-rules-reference.md](./docs/all-rules-reference.md).

---

## Quick Rule Lookup Matrix

| Category | Prefix | Focus Area & Key Rules |
| :--- | :--- | :--- |
| **Architecture** | `arch-` | [Feature Modules](./rules/arch-feature-modules.md), [Circular Deps](./rules/arch-avoid-circular-deps.md), [Single Responsibility](./rules/arch-single-responsibility.md), [Module Sharing](./rules/arch-module-sharing.md) |
| **Dependency Injection** | `di-` | [Constructor Injection](./rules/di-prefer-constructor-injection.md), [Avoid Service Locator](./rules/di-avoid-service-locator.md), [Provider Scopes](./rules/di-scope-awareness.md), [Tokens](./rules/di-use-interfaces-tokens.md) |
| **Security** | `security-` | [Validation & DTOs](./rules/security-validate-all-input.md), [Guards](./rules/security-use-guards.md), [JWT Auth](./rules/security-auth-jwt.md), [Rate Limiting](./rules/security-rate-limiting.md), [Output Sanitization](./rules/security-sanitize-output.md) |
| **Database & ORM** | `db-` | [Transactions](./rules/db-use-transactions.md), [Avoid N+1](./rules/db-avoid-n-plus-one.md), [Migrations](./rules/db-use-migrations.md) |
| **Performance** | `perf-` | [Caching](./rules/perf-use-caching.md), [DB Query Optimization](./rules/perf-optimize-database.md), [Lazy Loading](./rules/perf-lazy-loading.md), [Async Hooks](./rules/perf-async-hooks.md) |
| **Testing** | `test-` | [Supertest E2E](./rules/test-e2e-supertest.md), [Testing Module](./rules/test-use-testing-module.md), [Mocking Services](./rules/test-mock-external-services.md) |
| **Error Handling** | `error-` | [Exception Filters](./rules/error-use-exception-filters.md), [HTTP Exceptions](./rules/error-throw-http-exceptions.md), [Async Errors](./rules/error-handle-async-errors.md) |
| **API Design** | `api-` | [DTO Serialization](./rules/api-use-dto-serialization.md), [Pipes](./rules/api-use-pipes.md), [Interceptors](./rules/api-use-interceptors.md), [Versioning](./rules/api-versioning.md) |
| **Microservices** | `micro-` | [Message Patterns](./rules/micro-use-patterns.md), [Health Checks](./rules/micro-use-health-checks.md), [Background Queues](./rules/micro-use-queues.md) |
| **DevOps** | `devops-` | [Config Module](./rules/devops-use-config-module.md), [Structured Logging](./rules/devops-use-logging.md), [Graceful Shutdown](./rules/devops-graceful-shutdown.md) |

---

## Verification & Audit

Before declaring completion of any NestJS task, execute the deterministic audit script:

```bash
./scripts/audit-nestjs.sh src/
```
