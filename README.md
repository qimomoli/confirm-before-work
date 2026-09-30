# Confirm Before Work

`confirm-before-work` is an agent skill that adds a confirmation gate before an AI coding agent writes files.

It is designed for people who want an agent to move fast during reading, searching, and analysis, but slow down at the point where mistakes become expensive: creating, editing, overwriting, deleting, or indirectly generating files on disk.

The skill makes the agent restate the intended file action, target files, assumptions, boundaries, open questions, and likely side effects before it writes. That extra checkpoint helps prevent task drift, misunderstood requirements, accidental edits, and silent file changes.

## What It Does

- Triggers before direct or indirect file-system mutations.
- Requires a concise, structured understanding check.
- Names the target files, directories, or bounded patterns before they are changed.
- Includes generated artifacts and other likely indirect side effects.
- Separates read/search/analysis from write operations.
- Waits for explicit user approval before creating, editing, overwriting, or deleting files.
- Requires a new confirmation when the approved scope changes.

## Why It Helps

AI agents can correctly inspect a codebase but still write the wrong thing because the task boundary shifted, an assumption was wrong, or the user meant a narrower change.

This skill adds a small pause exactly before the write. The agent can still investigate normally, but must confirm the mutation and its scope before it touches the filesystem.

## Safety Model

This is a workflow guardrail, not a file-system sandbox. It improves human control
when the agent follows the rule, but it cannot technically prevent an agent or
tool from writing files. Use operating-system permissions, isolated worktrees,
backups, and review tools when stronger enforcement is required.

## What Counts As A Write?

The confirmation gate covers:

- Creating, editing, overwriting, deleting, renaming, or moving files.
- Formatters, code generators, migrations, and tests that modify the workspace.
- Lockfiles, snapshots, coverage reports, build output, caches, indexes, and
  other generated artifacts.
- Repository metadata or working-tree changes, including operations that alter
  the index or tracked files.
- Any command whose file-system side effects are uncertain.

Reading, searching, listing, inspecting status or diffs, reasoning, and drafting
in chat are normally read-only. If a read-like command can create logs, caches,
temporary files, or generated output, the agent should treat it as a write.

## Authorization Semantics

A confirmation applies only to the action, targets, and boundaries named in the
immediately preceding understanding check. The agent must ask again if it needs
additional files, a broader pattern, a different operation, a destructive
change, or an unlisted side effect.

The original task request is not a substitute for the understanding check.
Silence, a topic change, or an ambiguous response is not approval.

## Confirmation Format

Before writing files, the agent should say:

```text
File action I am about to take:
- ...

Target file(s), directory(ies), or file pattern(s):
- ...

Intended change:
- ...

Potential indirect side effects:
- ...

Boundary and assumptions:
- ...

What is still unclear:
- ...

Please confirm before I write these files.
```

The target list may use a clearly bounded pattern such as `src/**/*.ts`, but
the agent should not hide an unknown or unbounded scope behind a broad pattern.

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

Please confirm before I write this file.
```

### Implicit write

Before running a formatter, generator, build, migration, or test command, the
agent should identify files that may be changed. A command that appears to
operate on source code still needs confirmation if it can produce a lockfile,
snapshot, report, cache, or other artifact.

### Scope expansion

If the user approved `README.md` and the agent later discovers that
`docs/install.md` must also change, the agent should stop and request a new
confirmation for the additional file. The first approval does not cover it.

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

## Scope

This skill is intentionally narrow. It governs workspace and repository
mutations, not ordinary conversation.

It does not provide technical enforcement. Agent runtimes should pair it with
appropriate permissions and isolation when accidental writes would be costly.

## License

MIT
