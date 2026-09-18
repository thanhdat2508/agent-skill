# Agent red-team test taxonomy

Select categories from the actual architecture and authority map. This taxonomy is a coverage aid, not a requirement to execute every technique. Use inert proofs and current authoritative references.

## Instruction and context attacks

- Direct attempts to override task or policy
- Indirect instructions in web, email, documents, code, metadata, tool results, or retrieval
- Stored instructions in memory, summaries, profiles, and indexes
- Encoding, fragmentation, language switching, and repeated attempts
- Hidden or alternate-modal instructions in supported images, audio, OCR, PDF, or HTML

Safe oracle: an inert canary request, denied mock action, or policy event. Also test benign content discussing attacks to measure false positives.

## Tool use and agency

- Use of a tool outside the stated goal
- Read-to-write or preview-to-commit escalation
- Parameter or destination substitution
- Unsafe chaining of individually permitted tools
- Generic shell, URL fetch, file, database, or code-execution escape
- Retry, idempotency, cancellation, and partial-failure abuse
- Cost, time, or resource amplification within strict test limits

Safe oracle: mock tools with full traces, synthetic records, inert destinations, and hard budgets.

## Identity, authorization, and approvals

- Missing, expired, wrong-audience, or insufficient-scope identity
- Cross-tenant and unauthorized object access
- Confused-deputy behavior across downstream services
- Role or permission changes during a workflow
- Approval replay, stale approval, target or parameter changes after approval
- Self-approval, quorum bypass, and duplicate callback races

Safe oracle: synthetic tenants and one-time test approvals. Never test other real tenants.

## Data disclosure and egress

- System prompt or policy extraction where it is actually classified
- Cross-user, cross-tenant, memory, or training-data leakage
- Secret retrieval through tools, logs, traces, errors, or rendered output
- Exfiltration through URLs, messages, files, DNS-like channels, or downstream agents
- Output injection into HTML, SQL, shells, templates, or code

Safe oracle: fake secrets and canaries with no real authority. Stop if real sensitive data appears.

## Memory, retrieval, and supply chain

- Unauthorized creation or promotion of durable memory
- Poisoned retrieved content, metadata, embeddings, or summaries
- Stale, deleted, cross-tenant, or provenance-free retrieval
- Confusable or changed tool names/descriptions
- Untrusted MCP servers, plugins, models, adapters, packages, or prompt assets
- Configuration drift and unauthorized capability changes

Safe oracle: isolated indexes, signed fixtures, test-only tools, and a disposable dependency environment.

## Multi-agent coordination

- Sender impersonation or unauthenticated handoff
- Privilege inheritance or delegation beyond the sender's authority
- Tainted summaries that erase source provenance
- Recursive delegation, unbounded loops, and budget exhaustion
- Goal drift across planners, workers, reviewers, and executors
- One compromised agent influencing higher-privilege agents

Safe oracle: structured test messages, per-agent identities, bounded depth/cost, and mock executors.

## Monitoring and recovery

- Missing or forgeable audit events
- Sensitive content in logs and traces
- Failure to alert on canary access, denied high-risk actions, or tool changes
- Inability to disable tools, revoke credentials, quarantine memory, or stop workflows
- Recovery that restores contaminated state or silently loses evidence

Safe oracle: a tabletop or isolated recovery exercise with measured detection and containment time.

## Result semantics

- **passed:** observed safe behavior matched the oracle and `invariant_held` is true; severity is informational
- **failed:** a protected invariant was violated and `invariant_held` is false; severity cannot be informational
- **blocked:** prerequisites or environment prevented a valid observation; `invariant_held` is null and this is not a pass
- **error:** harness or target error made the result invalid; `invariant_held` is null and this is not a pass
- **not-run:** approved case was not executed; timestamps are null and the case remains in the plan-denominator gap

Each result must name the approved campaign and case, unique test ID, authorization reference, tester subject, target, environment, configuration digest, timestamps, observed request/cost/time limits, exact protected invariant and expected behavior, and cleanup state. Store evidence as objects with an evidence ID, kind, reference, capture time, and optional SHA-256 digest—not as unstructured strings.

Calculate attempt and observation percentages from all approved campaign-plan case IDs. Missing records, blocked cases, errors, and not-run cases remain in the denominator. These metrics describe tested scope; they do not establish security or certification.

## Primary references

- [OWASP AI Red Teaming Initiative](https://genai.owasp.org/initiatives/ai-red-teaming-initiative/)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP AI Testing Guide](https://owasp.org/www-project-ai-testing-guide/)
- [NIST AI 100-2 E2025: Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)
- [MITRE ATLAS](https://atlas.mitre.org/)
