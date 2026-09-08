# Confirm Before Work

`confirm-before-work` is an agent skill that adds a confirmation gate before an AI coding agent writes files.

It is designed for people who want an agent to move fast during reading, searching, and analysis, but slow down at the point where mistakes become expensive: creating, editing, overwriting, or deleting files on disk.

The skill makes the agent restate the intended file action, target files, assumptions, boundaries, and open questions before it writes. That extra checkpoint helps prevent task drift, misunderstood requirements, accidental edits, and silent file changes.

## What It Does

- Triggers when the next step would modify files on disk.
- Requires a concise, structured understanding check.
- Names the target files before they are changed.
- Separates read/search/analysis from write operations.
- Waits for explicit user approval before creating, editing, overwriting, or deleting files.

## Why It Helps

AI agents can correctly inspect a codebase but still write the wrong thing because the task boundary shifted, an assumption was wrong, or the user meant a narrower change.

This skill adds a small pause exactly before the write. The agent can still investigate normally, but must confirm the mutation before it touches the filesystem.

## Confirmation Format

Before writing files, the agent should say:

```text
File action I am about to take:
- ...

Target file(s):
- ...

Intended change:
- ...

Boundary and assumptions:
- ...

What is still unclear:
- ...

Please confirm before I write these files.
```

## Example

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

Boundary and assumptions:
- I will only change the install section.
- I will not change project behavior or code.

What is still unclear:
- Nothing.

Please confirm before I write this file.
```

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

Or rely on automatic skill discovery when your environment supports implicit skill selection.

## Repository Layout

```text
skills/
  confirm-before-work/
    SKILL.md
    agents/
      openai.yaml
```

## Scope

This skill is intentionally narrow. It is for file writes, not ordinary conversation.

Reading files, searching, reasoning, drafting in chat, and explaining plans do not count as file writes.

## License

MIT
