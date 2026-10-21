# Confirm Before Work

`confirm-before-work` is an agent skill that adds a confirmation gate before an AI coding agent performs consequential local or external actions.

It is designed for people who want an agent to move fast during reading, searching, and analysis, but slow down at the point where mistakes become expensive: changing files, repositories, services, databases, cloud resources, external systems, or public communication channels.

The skill makes the agent restate the intended action, targets, assumptions, boundaries, open questions, and likely side effects before it acts. That extra checkpoint helps prevent task drift, misunderstood requirements, accidental edits, silent file changes, and unintended external actions.

## What It Does

- Triggers before direct or indirect local or external side effects.
- Requires a concise, structured understanding check.
- Names the target files, directories, repositories, services, resources,
  endpoints, or bounded patterns before they are changed.
- Includes generated artifacts and other likely indirect side effects.
- Separates read/search/analysis from side-effecting operations.
- Waits for explicit user approval before creating, editing, overwriting, deleting,
  publishing, sending, restarting, provisioning, or otherwise changing state.
- Requires a new confirmation when the approved scope changes.

## Why It Helps

AI agents can correctly inspect a codebase but still write the wrong thing because the task boundary shifted, an assumption was wrong, or the user meant a narrower change.

This skill adds a small pause exactly before the side effect. The agent can
still investigate normally, but must confirm the action and its scope before it
touches local or external state.

## Safety Model

This is a workflow guardrail, not a file-system sandbox. It improves human control
when the agent follows the rule, but it cannot technically prevent an agent or
tool from writing files. Use operating-system permissions, isolated worktrees,
backups, and review tools when stronger enforcement is required.

## What Counts As A Side Effect?

The confirmation gate covers:

- Creating, editing, overwriting, deleting, renaming, or moving files.
- Formatters, code generators, migrations, and tests that modify the workspace.
- Lockfiles, snapshots, coverage reports, build output, caches, indexes, and
  other generated artifacts.
- Repository metadata or working-tree changes, including operations that alter
  the index or tracked files.
- Any command whose file-system side effects are uncertain.
- Outbound network requests that change or submit external state.
- Database writes and migrations.
- Cloud-resource provisioning, updates, deletion, or permission changes.
- Service starts, stops, restarts, deployments, or runtime configuration changes.
- Messages, comments, appointments, and other representational communication.
- Git pushes, pull requests, releases, package publication, and other code
  publication.

Reading, searching, listing, inspecting status or diffs, reasoning, and drafting
in chat are normally read-only. Read-only inspection of external systems is also
normally allowed when it does not change state or transmit user data. If a
read-like command can create logs, caches, temporary files, generated output,
or external state changes, the agent should treat it as a side effect.

## Authorization Semantics

A confirmation applies only to the action, targets, and boundaries named in the
immediately preceding understanding check. The agent must ask again if it needs
additional files, a broader pattern, a different operation, a destructive
change, a new destination, a new external system, or an unlisted side effect.

The original task request is not a substitute for the understanding check.
Silence, a topic change, or an ambiguous response is not approval.

## Confirmation Format

Before performing a side effect, the agent should say:

```text
Action I am about to take:
- ...

Target file(s), directory(ies), repository(ies), service(s), resource(s),
endpoint(s), or bounded pattern(s):
- ...

Intended change:
- ...

Potential indirect side effects:
- ...

Boundary and assumptions:
- ...

What is still unclear:
- ...

Please confirm before I perform this action.
```

The target list may use a clearly bounded pattern such as `src/**/*.ts`. For
path-like targets, `*` matches within one path segment and `**` may span
multiple segments. Parent-directory (`..`) segments and unbounded target
patterns such as `*`, `**`, and `**/*` are invalid.

## Examples

User:

```text
Update the README with install instructions.
```

Agent:

```text
File action I am about to take:
- Edit an existing Markdown file.

Target file(s):
- README.md

Intended change:
- Add install instructions.

Potential indirect side effects:
- None expected.

Boundary and assumptions:
- I will only change the install section.
- I will not change project behavior or code.

What is still unclear:
- Nothing.

Please confirm before I perform this action.
```

### Implicit write

Before running a formatter, generator, build, migration, or test command, the
agent should identify files that may be changed. A command that appears to
operate on source code still needs confirmation if it can produce a lockfile,
snapshot, report, cache, or other artifact.

### External side effect

Before sending a request, changing a database or cloud resource, restarting a
service, sending a message, pushing code, or opening a pull request, the agent
should identify the destination, operation, intended payload or state change,
and likely side effects. Read-only inspection is allowed when it does not
change state or transmit user data.

### Scope expansion

If the user approved `README.md` and the agent later discovers that
`docs/install.md` must also change, the agent should stop and request a new
confirmation for the additional file. The first approval does not cover it.
The same rule applies to a new operation, destination, external system, or
side-effect category.

## Install

Copy `skills/confirm-before-work` into your agent skills directory.

For Codex:

```powershell
Copy-Item -Recurse .\skills\confirm-before-work $env:USERPROFILE\.codex\skills\
```

For runtimes that support the shared skills path:

```powershell
Copy-Item -Recurse .\skills\confirm-before-work $env:USERPROFILE\.agents\skills\
```

## Usage

Invoke it explicitly:

```text
$confirm-before-work
```

Or rely on automatic skill discovery when your environment supports implicit skill discovery.

## Repository Layout

```text
skills/
  confirm-before-work/
    SKILL.md
    agents/
      openai.yaml
```

## Conformance Evaluations

The repository includes a dependency-free evaluator and checked-in cases:

```powershell
python -B .\evals\validate.py --cases .\evals\cases.json
```

The cases cover direct and indirect file operations, tooling artifacts, Git
operations, external side effects, read-only inspection, rejected approvals,
and scope expansion. See [`evals/README.md`](evals/README.md) for the trace
format and runtime adapter contract.

## Scope

This skill governs consequential workspace, repository, and external-system
mutations, not ordinary conversation.

It does not provide technical enforcement. Agent runtimes should pair it with
appropriate permissions and isolation when accidental changes or transmissions
would be costly.

## License

MIT
