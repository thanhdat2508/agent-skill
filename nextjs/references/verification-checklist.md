# Performance & Quality Verification Checklist

Use this audit checklist before releasing code changes or submitting pull requests.

---

## 1. Network & Bundle Audit
- [ ] No barrel imports in critical paths (`lucide-react`, `@mui`, lodash).
- [ ] Heavy third-party scripts loaded with `lazyOnload` or after hydration.
- [ ] Dynamic components (`next/dynamic`) used for off-screen modals, charts, and rich-text editors.
- [ ] Client JS bundle size for landing pages remains under **300 KB** (gzip).

## 2. Core Web Vitals Audit
- [ ] **LCP (≤ 2.5s):** Hero image has `priority` / `fetchpriority="high"`.
- [ ] **INP (≤ 200ms):** No long tasks (> 50ms) blocking user input; heavy filters use `startTransition` or `useDeferredValue`.
- [ ] **CLS (≤ 0.1):** All images and video containers define explicit `width`, `height`, or `aspect-ratio`.
- [ ] **Speculation Rules:** Implemented for top navigation paths with moderate eagerness.

## 3. Server-First, Separation of Concerns & Code Health Audit
- [ ] **Layer Ownership and Placement:** Each piece of logic resides in the correct architectural tier (DAL services for database/external access, custom hooks for interactive client state, leaf components for DOM binding, pure utilities for data formatting).
- [ ] **Thin Components & Pages:** Component files remain pure view orchestrators (< 150-200 lines); no heavy math, complex filtering algorithms, or raw schema transformations inline.
- [ ] **Data Logic Extracted to `lib/services/` (DAL):** Database queries (Prisma/ORM/SQL), external APIs, and business calculations live in dedicated service modules outside component files.
- [ ] **Client Logic Extracted to Custom Hooks (`hooks/`):** Complex client state machines, debouncing, pagination, and form handling extracted into reusable custom hooks.
- [ ] **No Unnecessary `'use client'`:** Pages, layouts, and data containers remain pure Server Components; `'use client'` is strictly pushed to leaf interactive buttons/inputs.
- [ ] **Zero `useEffect` for Data Fetching:** Data is fetched directly on the server or via Server Actions (never inside a client `useEffect` lifecycle).
- [ ] **Zero `useEffect` for Derived State:** Computed values calculated directly in render body or wrapped in `useMemo()`.
- [ ] **Zero `useEffect` for User Events:** Business logic triggered directly in event handlers (`onClick`, `onSubmit`), not via state watchers.
- [ ] **Independent server requests** parallelized with `Promise.all()`.
- [ ] **Sensitive database queries** kept inside Server Components.
- [ ] **Long list items** leverage CSS `content-visibility: auto`.
- [ ] **Zero hydration warnings** in developer console.

## 4. Edge & Caching
- [ ] Static or semi-static pages configured with ISR or caching headers.
- [ ] Database requests deduplicated with `React.cache()`.

## 5. TypeScript Discipline Audit
- [ ] **No `any` or Unearned `as`:** External data is typed as `unknown`; casts only occur after boundary validation.
- [ ] **Discriminated Unions for States:** Loading/Error/Success states modeled with literal discriminants, no optional-field bags.
- [ ] **Boundary Schema Validation:** Server Actions and Route Handlers validate input via Zod/schemas, with types inferred via `z.infer`.
- [ ] **Branded Types for IDs:** Sensitive domain identifiers (User IDs, Org IDs, Token strings) branded to prevent cross-assignment.
- [ ] **Exhaustiveness Checked:** Switch statements over unions feature an inline `const _exhaustive: never = state;` default arm.
- [ ] **Types as Constructions & Total Functions:** Types constructed so impossible values cannot be built; functions made total by pushing invariants into types rather than defensive throws.

## 6. Code Documentation Integrity Audit
- [ ] **Zero Meaningless / Obvious Comments:** No comments narrating trivial code (`// render button`, `// fetch user`, `// state for open`).
- [ ] **Zero Dead Commented-Out Code:** No commented-out legacy code blocks left behind.
- [ ] **High-Signal "WHY" Explanations:** Comments solely document non-obvious business logic, browser workarounds, or performance rationales.
- [ ] **Strict Freshness:** Every comment strictly matches the current codebase implementation; zero stale comments.

## 7. Unslop Writing and Communication Audit
- [ ] **Zero AI Buzzwords:** Documentation and comments avoid buzzwords ("crucial", "pivotal", "delve", "foster", "testament", "tapestry", "landscape", "enhance").
- [ ] **Plain Speech Over Metaphor:** Mechanisms and numbers are stated directly instead of emotional feelings ("runs in 15ms" instead of "lightning-fast").
- [ ] **Clean Typography:** Zero decorative emojis in headings; periods or commas used instead of em dashes.
- [ ] **Active Voice:** Sentences use active voice with named actors.

## 8. Foundational Principles & Verification Audit
- [ ] **Root-Cause Fixes:** Bugs resolved at the root origin rather than masked with downstream optional chaining (`?.`) or silent null guards.
- [ ] **Data Structures Precede Logic:** Core domain types, schemas, and state representations finalized before UI implementation.
- [ ] **Subtraction Precedes Scaffolding:** Unused code, dead components, and obsolete dependencies deleted prior to introducing new architecture.
- [ ] **Prove It Works:** Tasks verified against real artifacts, running feature paths, or deterministic check scripts; not proxy mtimes or "it compiles".
- [ ] **Test Behavior, Not Implementation:** Tests assert literal user-visible outputs against concrete inputs; tests fail if imported functions return `undefined`; zero weak assertions (`toBeDefined`) or constant pins.
- [ ] **Laziness Protocol:** Call hierarchies remain flat (< 3 layers); branching consolidated behind single-source flags; diff sizes minimized; zero signal threading through unnecessary layers.
- [ ] **Attack the Premise:** When multiple fixes fail under a shared assumption, record the premise, measure actor skew, and remove structural asymmetry.
- [ ] **Verification Skill Upkeep:** Feature map verified against current codebase; no doc drift; live instances verified with health checks; test residue cleaned up.
- [ ] **Minimize Reader Load:** Pass-through wrappers collapsed, call chains kept under 3 layers, mutable state minimized, and 30-second trace test passes.
- [ ] **Adversarial Interrogation:** High-impact changes challenged across diverse models or angles, consensus issues addressed, zero unexamined blind spots.
- [ ] **Model the Domain:** Domain invariants encoded into typed data structures or state machines; zero scattered boolean flags or synchronized state pairs.
- [ ] **Unblocked Execution:** Autonomous momentum maintained on reversible actions without unnecessary pauses; human informed via verified output.
- [ ] **Outcome-Oriented Migrations:** Direct convergence on target architecture without temporary throwaway compatibility debt.
- [ ] **First-Principles Integration:** New requirements architected holistically from the ground up across all affected layers, rather than bolted on as ad hoc patches.
- [ ] **Verifiable Unit Sequencing:** Work decomposed into atomic, verifiable before/after brackets (red-to-green per unit); delivery stacked to prove correctness.
- [ ] **Subtract Before Adding:** Dead code, obsolete flags, and redundant validators eliminated prior to adding new architectural logic.
- [ ] **Migrate Callers & Delete Legacy APIs:** Deprecated internal hooks, components, and utilities removed alongside caller migration; zero dual-path legacy shims.
