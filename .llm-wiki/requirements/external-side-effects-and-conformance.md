# External Side Effects and Conformance

## Why

`confirm-before-work` currently describes a useful confirmation gate, but its
behavior is not represented by executable conformance cases and its scope is
centered on local file-system mutations. This change makes the policy
measurable and extends the same human-approval boundary to other consequential
agent actions.

## What Changes

- Add a dependency-free conformance case set covering direct, indirect, local,
  repository, and external side effects.
- Add a validator for structured agent traces.
- Document the trace format, expected outcomes, and local verification command.
- Treat network requests, database writes, cloud-resource changes, service
  control, outbound messages, and code publication as confirmation-gated
  side effects.
- Keep read-only inspection and analysis outside the confirmation gate.
- Synchronize the repository skill and the installed local skill.

## Non-Goals

- No runtime sandbox, OS permission layer, or tool interception mechanism.
- No provider-specific model API integration.
- No real network, database, cloud, service, messaging, or GitHub mutations
  during conformance evaluation.
- No changes to repository permissions, GitHub metadata, or remote state.

## Active Scope

- `evals/cases.json`
- `evals/validate.py`
- `evals/README.md`
- `README.md`
- `skills/confirm-before-work/SKILL.md`
- `skills/confirm-before-work/agents/openai.yaml`
- The matching installed skill files under the local Codex skills directory.

## Acceptance Criteria

1. The conformance suite covers direct file edits, shell redirection and
   scripts, formatter/build/snapshot output, lockfiles/caches, Git index and
   publication operations, destructive and batch file operations, and indirect
   tool-chain writes.
2. The conformance suite covers network, database, cloud, service-control,
   outbound-message, and code-publication side effects.
3. Approved traces pass; effects before approval, unapproved effects, and
   scope expansion without a new approval fail.
4. Read-only traces pass without requiring confirmation.
5. The validator uses only the Python standard library and does not mutate the
   workspace when invoked with `python -B`.
6. Repository and installed skill rules describe the same confirmation model.

## Verification Plan

- Run the validator against the checked-in cases.
- Run focused negative probes for an effect before approval and for an effect
  outside the approved scope.
- Inspect the final diff and compare the repository skill with the installed
  skill.

## Flow Record

| Stage | Status | Evidence |
| --- | --- | --- |
| Requirement | active | This Change Brief |
| Design | complete | In-chat approved design |
| Development | complete | `evals/validate.py`, `evals/cases.json`, skill and README updates |
| Testing | complete | 19/19 conformance cases; syntax/JSON checks; two negative probes rejected |
| Finish | pending | No commit or remote operation in scope |
