# Technical Writing & Code Documentation Guidelines (Unslop) for NestJS

Guidelines for clear, professional, fluff-free technical writing in NestJS backend codebases, comments, and PR documentation.

---

## 1. Eliminate Artificial AI Jargon

AI models frequently inflate documentation with decorative corporate vocabulary. Strip these terms from all technical writing, code docstrings, and commit messages:

| Banned AI Word | Preferred Engineering Alternative |
|:---|:---|
| *crucial / pivotal* | important / necessary / required |
| *delve / dive into* | examine / inspect / review |
| *foster / cultivate* | build / support / create |
| *testament to* | evidence of / shows |
| *tapestry / landscape* | system / architecture / ecosystem |
| *enhance* | improve / speed up / optimize |
| *seamless / friction-free* | direct / automatic |
| *robust / cutting-edge* | tested / verified / typed |

---

## 2. State Mechanisms and Concrete Metrics

Describe backend code through concrete mechanisms and benchmark figures rather than emotional descriptions:

- ❌ *"Implements a lightning-fast, ultra-robust Redis caching layer to foster optimal throughput."*
- ✅ *"Caches serialized user profiles in Redis with a 60-second TTL, reducing database reads by 82% under peak load."*

- ❌ *"Uses cutting-edge database connection pooling to ensure seamless scalability."*
- ✅ *"Sets PostgreSQL pool size to 20 connections with a 5,000ms idle timeout to prevent connection exhaustion during traffic spikes."*

---

## 3. Clean Typography & Heading Rules

- **Zero Decorative Emojis in Headings:** Keep markdown headers clean and professional (`# Architecture Overview`, not `# 🚀 Architecture Overview ✨`).
- **No Em Dashes:** Replace em dashes (`—`) with standard periods, colons, or commas.
- **Active Voice:** Name the actor directly: *"The AuthGuard validates the JWT token"* rather than *"The JWT token is validated by the AuthGuard"*.

---

## 4. Code Comment Hygiene

### Rule 1: Zero Meaningless / Obvious Comments
Never write comments that merely restate what the code already says:

```typescript
// ❌ ANTI-PATTERN: Obvious comments narrating trivial syntax
// Inject user repository
constructor(
  // The user repository instance
  private readonly userRepo: UserRepository,
) {}

// Method to find all users
async findAll() {
  // Call repository
  return this.userRepo.find(); // Return users
}
```

### Rule 2: Zero Commented-Out Dead Code
Never commit commented-out code blocks (`// const oldQuery = await ...`). Rely on Git history. Dead code clutters context and confuses AI coding agents.

### Rule 3: Document the "WHY", Not the "WHAT"
Only write comments that explain non-obvious business logic, database query trade-offs, or upstream workarounds:

```typescript
// ✅ BEST PRACTICE: Explaining non-obvious business constraints and concurrency choices
// Advisory lock key 4029 isolates concurrent invoice creation per organization
// to prevent duplicate billing charges during network retries.
await this.db.$executeRaw`SELECT pg_advisory_xact_lock(4029, ${orgId})`;
```

### Rule 4: Mandatory Freshness
A comment that describes an outdated implementation is treated as a critical bug. When refactoring code, always update or remove associated comments.
