# Authorized agent red-team campaign

## Authorization and rules of engagement

- Target owner:
- Authorization status, reference, approver subject, approval time, and expiry:
- Exact target IDs, environment, version, and configuration SHA-256 digest:
- Test window and stable tester subject IDs:
- Allowed techniques:
- Prohibited systems, data, techniques, and effects:
- Rate, time, and cost ceilings:
- Stop conditions:
- Emergency contact and channel:
- Evidence location, access, retention, and deletion:
- Cleanup owner and deadline:

If authorization is pending, label this plan non-executable.

Mirror the approved fields and case IDs in [campaign-plan-template.json](campaign-plan-template.json). The JSON plan is the authority used by `score_campaign.py`; prose notes cannot add executable scope.

## System and privilege map

- Models and orchestration:
- Inputs and retrieval:
- Memory:
- Tools and external systems:
- Identities, scopes, tenants, and approvals:
- Protected assets and security invariants:
- Output sinks:

## Test matrix

| Approved case ID | Hypothesis/category | Target / environment / config digest | Preconditions | Protected invariant | Safe case/oracle | Expected safe behavior | Per-case limits | Cleanup required |
| ---------------- | ------------------- | ------------------------------------ | ------------- | ------------------- | ---------------- | ---------------------- | --------------- | ---------------- |
|                  |                     |                                      |               |                     |                  |                        |                 |                  |

## Execution log

| Case ID / test ID | Authorization reference | Tester | Target / environment / config digest | Started / ended / recorded | Observed limits | Outcome / invariant held | Structured evidence IDs | Cleanup status / evidence |
| ----------------- | ----------------------- | ------ | ------------------------------------ | -------------------------- | --------------- | ------------------------ | ----------------------- | ------------------------- |
|                   |                         |        |                                      |                            |                 |                          |                         |                           |

## Findings

For each finding record title, approved case ID, unique test ID, affected target/configuration, protected invariant, severity rationale, prerequisites, minimum safe reproduction, expected/observed behavior, structured evidence, root control failure, containment, durable remediation, owner, and regression test. A failed invariant cannot be informational; non-failed outcomes do not carry finding severity.

## Retest and closure

- Findings retested:
- Nearby variants:
- Benign utility and false positives:
- Open or accepted risk and owners:
- Synthetic records removed:
- Test credentials revoked:
- Jobs/callbacks stopped:
- Fixtures restored:
- Unexpected effects or incident reference:

Report attempted and observed percentages against every approved plan case, including missing and explicitly not-run cases in the denominator. Do not label a submitted-record ratio as campaign coverage, and do not describe the result as proof of security or certification.
