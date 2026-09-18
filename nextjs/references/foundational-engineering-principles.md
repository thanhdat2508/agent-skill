# Foundational Engineering Principles for Next.js & React

Core engineering principles governing root-cause problem solving, architectural planning, and session token efficiency.

---

## 1. Fix Root Causes, Not Symptoms

When debugging performance regressions, hydration mismatches, or runtime exceptions:

- **Trace every symptom to its root cause:** Fix the failure at its origin rather than patching downstream effects.
- **Resist defensive guard patches:** Adding a `?.` or null check to silence a crash often masks a broken data fetch, an unvalidated schema, or a missing database relation. Fix the upstream query or boundary validation instead.
- **Reproduce before patching:** Form a concrete hypothesis, verify it with metrics or reproduction steps, and confirm the fix eliminates the error.
- **Check for the pattern:** When a bug is found (for example, an unhandled Promise rejection or missing passive listener), grep across the codebase to fix all occurrences, not just the single file where the bug was reported.
- **Suspect state before code in restart/re-render bugs:** If an issue occurs on page reload or re-render, suspect stale persistent state first (browser `localStorage`, CDN edge cache, ISR tags, or un-invalidated cookies).

---

## 2. Foundational Thinking: Data Structures and Scaffolding First

- **Data structures precede UI logic:** Model the core TypeScript types, discriminated unions, and domain schemas before writing React components or JSX layouts. When data structures match the dominant access patterns, component logic becomes straightforward and declarative.
- **Subtraction before scaffolding:** Remove obsolete code, unused dependencies, and dead components before laying new architectural foundations.
- **Scaffold before features:** Establish TypeScript types, data access layers (DAL), error boundaries, and test helpers before implementing feature UI.
- **Concurrency and shared state isolation:** Before sharing state across components or Server Actions, ask what happens if two requests or user interactions mutate it concurrently. If state cannot be safely mutated concurrently, isolate it.
- **Avoid premature abstractions:** Three similar lines of code beat a hasty, leaky abstraction. Abstract only when boundaries and reuse patterns are clearly proven.

---

## 3. Guard the Context Window

Context tokens are finite and non-renewable within an AI agent session:

- **Isolate large payloads:** When running broad performance audits, bundle analyzers, or Lighthouse scans, extract high-level summaries and actionable metrics rather than dumping megabytes of raw JSON logs into context.
- **Read selectively:** Read files with targeted line ranges rather than pulling entire massive files into the prompt.
- **Cap scope per phase:** Complete modular milestones sequentially. Avoid unbounded, multi-directory refactorings in a single turn.

---

## 4. Prove It Works

Verify every task output by checking the real artifact directly:

- **Never infer from proxies:** Do not trust file timestamps, build completion messages, or agent self-reports alone. Check the actual running system or generated artifact.
- **Verify full data path:** Exercise the actual code path: does data flow from user interaction or API trigger down through the Server Component, DAL, database, and back to the rendered DOM?
- **Script the verification check:** The strongest verification is a deterministic, automated script (`audit-performance.sh`, Vitest suite, Playwright script) that can be re-executed consistently.
- **Inspect actual diffs and outputs:** When delegating tasks to subagents, audit the real git diff and output files, not the summary returned by the subagent.

---

## 5. Test Behavior, Not Implementation

A test calls the code the way its users do and asserts the result they observe against a literal expected value:

- **The Undefined Check:** Before keeping a test, ask if it would still pass if every imported function returned `undefined`. If yes, the test observes zero behavior. Rewrite or delete it.
- **Ban weak or absence-only assertions:** Avoid tests that only call `toBeDefined()`, `toBeTruthy()`, `toBeInstanceOf()`, `toHaveBeenCalled()`, or `toHaveLength(0)`.
- **Ban constant pinning:** Never assert against hardcoded configuration constants, prompt strings, or internal variables (`expect(LIMITS.maxTools).toBe(8)`). Test the actual mechanism consuming the constant.
- **Assert literal values:** Call functions with concrete inputs and assert exact outputs (`expect(formatCurrency(1500)).toBe("$15.00")`).
- **Test observable DOM outcomes:** In React component tests, assert user-visible states (rendered text, accessible roles, displayed error banners) rather than internal hook states or mocked render counts.

---

## 6. Laziness Protocol

Maximize results while minimizing code and structural complexity:

- **Bias toward deletion:** When refactoring, actively seek removals and simplifications before adding new abstractions.
- **Maintain a flat call hierarchy:** Keep call depth under 3 layers or files. If tracing a value requires drilling through more than 3 intermediary layers, flatten the architecture.
- **Consolidate branching decisions:** Put repeated checks behind a single source of truth and pass a simple flag or discriminant.
- **Minimize diffs:** Always prefer the smallest change that solves the root problem. Minimal lines beat complex boilerplate.
- **Question signal threading:** Avoid threading props, flags, or parameters through multiple intermediate components or schemas when a direct composition or Server Component structure exists.
- **Eliminate representation leaks:** Remove tiny pass-throughs and leaky wrappers before they spread across the codebase.

---

## 7. Attack the Premise

When two or more attempted fixes that share a premise fail the same test or audit gate:

- **Write down the shared premise:** Explicitly state the underlying assumption common to all failed attempts.
- **Census actor imbalance:** Measure which components, actors, or routes hold the imbalance or failure load.
- **Analyze skew:** If specific actors consistently fail, find what assigns them that role instead of writing another compensating workaround.
- **Eliminate structural asymmetry:** Remove the asymmetric burden directly (e.g., randomize assignment, decouple shared state, or eliminate unnecessary synchronization) instead of adding compensatory code.
- **Stop before retrying:** Never launch a third fix that relies on the same invalidated premise.

---

## 8. Maintain Verification Systems and Feature Maps

Keep project-local verification skills and feature documentation aligned with the running app:

- **Feature-level rigor:** Verify each user-facing feature against live application behavior and source code entry points.
- **Detect and fix doc drift:** When application behavior changes, update the verification map rather than masking regressions.
- **Doctor before driving:** Ensure dev servers, background processes, and databases pass health checks before driving end-to-end test scenarios.
- **Clean test residue:** Ensure no orphan processes, test databases, or dangling locks outlive the verification run.
- **Clear outcomes:** Explicitly report verification status as clean, changed, or blocked.

---

## 9. Minimize Reader Load

Code is read far more than it is written. Reader load is measured on two axes:

1. **Layers to trace:** The number of indirections between a question and its answer.
2. **State to hold:** The volume of mutable or hidden context a reader must hold in working memory.

- **Collapse low-value layers:** Inline single-caller wrappers, unused adapter layers, and speculative abstractions that do not change the level of abstraction.
- **Demand interface compression:** Ensure adjacent layers meaningfully compress complexity rather than merely passing arguments forward.
- **Shrink state scope:** Prefer pure functions with returned values over mutations; local variables over component state; component state over global stores. Always derive state during render rather than synchronizing it across effects.
- **Enforce the 30-second rule:** A new engineer must be able to answer "where does this value come from?" and "what can mutate it?" in under 30 seconds.

---

## 10. Adversarial Review & Interrogation

Challenge critical architectural, security, and performance changes from diverse angles before shipping:

- **Independent multi-model interrogation:** Have multiple distinct models review code changes against an identical objective rubric to expose blind spots without bias.
- **Synthesize consensus:** Prioritize issues surfaced by multiple reviewers independently as highest-signal concerns.
- **Pragmatic lead judgment:** Group findings into actionable buckets: **Act On** (critical correctness, security, or performance blockers), **Consider** (worthwhile tradeoffs), **Noted** (low-impact or context-dependent), and **Dismissed** (invalid or nitpicky).
- **Reject auto-applying unverified feedback:** Human and lead review must evaluate adversarial findings before modifying production code.

---

## 11. Model the Domain in Data Structures

Encode the real domain in a data structure instead of scattering it across conditionals:

- **Make invalid states unrepresentable:** Choose state machines, discriminated unions, and typed models rather than scattered boolean flags (`isLoading`, `isError`, `isSuccess`, `hasSubmitted`).
- **Eliminate branching with maps and registries:** Use lookup tables, handler maps, or record dictionaries instead of sprawling `if/else` chains repeated across multiple files.
- **Organize by domain knowledge, not execution phases:** Group code around domain concepts rather than sequential phases like `load -> validate -> transform -> save`. Execution order is not architectural ownership.
- **Avoid synchronized booleans:** Never introduce a second boolean flag that must be manually synchronized with a first boolean flag.

---

## 12. Never Block on the Human (Proceed, Then Present)

Human supervision is asynchronous; agents must maintain forward momentum on reversible work:

- **Proceed, then present:** Execute reversible engineering tasks (writing code, extracting hooks, refactoring queries), present the verified result, and allow the human to course-correct after the fact.
- **Don't ask permission on reversible work:** Avoid pausing execution to ask "Should I do X?". Perform X, state why it was done, and provide a diff.
- **Reserve questions for genuine ambiguity:** Solicit input only when user intent cannot be inferred from repository context, existing issues, or specifications.
- **Respect irreversible boundaries:** Always request confirmation before irreversible actions (deleting production data, force-pushing remote branches, triggering external notifications).

---

## 13. Outcome-Oriented Execution (Target Architecture Over Transitional Debt)

During planned migrations, rewrites, or framework upgrades, converge directly on the target architecture:

- **Target state integrity:** Prioritize the final verified end state over preserving temporary transitional stability.
- **Reject throwaway compatibility code:** Avoid authoring disposable shims or complex translation layers that exist solely to smooth intermediate steps; they frequently become permanent technical debt.
- **Accept planned, scoped intermediate breakage:** Keep high-signal static checks focused on actively touched areas while migrating, then execute full static and runtime verification upon plan completion.

---

## 14. Redesign from First Principles

When integrating a new requirement or capability into an existing architecture, do not bolt it on as an ad hoc patch:

- **Foundational question:** Ask: "If this requirement had existed from day one, how would we have designed this system from scratch?"
- **Holistic propagation:** Trace and update every affected layer: domain types, database schemas, API contracts, documentation, and UI view models.
- **Preserve option value:** Design the complete coherent architecture first, then deliver it through clean, modular increments rather than creating hybrid technical debt.

---

## 15. Sequence Work into Verifiable Units

Decompose complex tasks, migrations, and refactorings into small units that each terminate in a verifiable check:

- **Red-to-green incrementality:** Never advance to step N+1 while step N is failing or unverified. Localize breakage at the exact unit that caused it.
- **Before/after bracket:** Frame each unit as a clear bracket: established known-good baseline, single atomic change, verify passing state, then advance.
- **Stack for proof:** Order commits and PRs so the sequence proves correctness to a reviewer (failing test first, then the implementation; baseline capture first, then optimization; dead-code subtraction first, then the reshape).

---

## 16. Subtract Before You Add

When evolving or refactoring a system, remove complexity first, then build:

- **Sequence removal before construction:** Delete dead code, obsolete flags, redundant validators, and stub references before authoring new features.
- **Cut before you polish:** Strip the implementation down to its essential core before investing in optimization or styling.
- **Design for observed usage:** Avoid implementing speculative edge-case guards, theoretical converters, or unused adapters beyond what the specification requires.
- **Continual simplification investment:** Leave the system simpler and more capable behind a smaller or equivalent public surface.

---

## 17. Type-System Discipline (The Compiler as Proof Assistant)

Use the type checker as a formal proof assistant to eliminate runtime errors, impossible states, and unhandled variants:

- **Make illegal states unrepresentable:** Model state variants with discriminated unions rather than loose bags of optional fields. (e.g. `{ kind: 'open' } | { kind: 'done'; at: Date }` instead of `{ completed: boolean; completedAt?: Date }`).
- **Types as constructions, not restrictions:** Build types up from valid components rather than attempting to carve them out of loose types using runtime guards. (e.g. a valid time range is a start plus a duration, not two independently mutable timestamps).
- **Brand semantic primitives:** Ensure domain identifiers (`UserId`, `OrderId`) are not interchangeable strings. Validate at creation and trust downstream.
- **Parse external boundaries:** External data (API responses, JSON payloads, searchParams, database rows) is untyped until parsed through boundary schemas (Zod).
- **Never lie to the compiler:** Prohibit unearned `as` casts and `any` types. If the compiler cannot verify an invariant, prove it through validation or narrowing.
- **Enforce compile-time exhaustiveness:** Verify every sum type match has a fallback `const _exhaustive: never = state;` so adding new variants triggers immediate compile-time errors.
- **Strengthen types where partiality appears:** When a null check or runtime assertion is needed, push the invariant into the type system to make functions total.

---

## 18. Migrate Callers Then Delete Legacy APIs

When introducing a new internal component, custom hook, utility, or API route while old callers still exist:

- **Migrate and delete in the same wave:** Inventory all existing call sites, refactor them to the new API, and immediately delete the legacy implementation in the same atomic refactor.
- **Reject permanent compatibility shims:** Avoid keeping deprecated components or wrapper functions alive solely because internal callers exist. Dual-path architectures confuse developers and AI agents, slowing down future refactorings.
- **Eliminate append-only drift:** Treat internal frontend codebases as active living systems, not append-only logs. If no third-party consumers rely on backwards compatibility, delete the legacy surface completely.
- **Update tests to the new contract:** Rewrite test suites to assert the behavior of the new API, and delete tests that only protect pre-refactor implementation details.
