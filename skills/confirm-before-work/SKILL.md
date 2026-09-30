---
name: confirm-before-work
description: Use before any direct or indirect file-system mutation, requiring the assistant to restate the exact write scope and wait for explicit user confirmation.
---

# Confirm Before Work

## Overview
Use this skill whenever the next action may create, edit, overwrite, delete, rename,
move, or otherwise persist data to disk.

## Core Rule
Before the first write:

1. Stop before running the write-capable action.
2. State the file action you are about to take.
3. List the target file(s), directories, or file patterns.
4. State the intended change and any likely indirect side effects.
5. State boundaries, assumptions, and open questions.
6. Ask for explicit confirmation.
7. Wait for a clear affirmative response before writing.

The user's original request is not, by itself, confirmation of the
understanding check. The check exists to confirm that the proposed mutation
matches the request.

## Scope
Apply this to direct and indirect mutations, including:

- Creating, editing, overwriting, deleting, renaming, or moving files.
- Commands that generate or update lockfiles, snapshots, reports, coverage data,
  build output, caches, indexes, or other artifacts.
- Formatters, code generators, migrations, and tests that can modify the
  workspace.
- Repository metadata or working-tree changes, such as operations that alter
  the index or tracked files.
- Batch operations whose exact file list is discovered only while they run.

Treat an action as write-capable when its side effects are uncertain. Inspect
or explain the command first, then ask before running it if it may persist
anything.

The following are normally read-only and do not need confirmation:

- Reading files, searching, listing, and inspecting status or diffs.
- Reasoning, drafting, summarizing, or explaining in chat.
- Commands that are known to be read-only and have no generated output.

If a supposedly read-only command may create logs, caches, temporary files, or
other artifacts, treat it as write-capable.

## Authorization Boundaries
A confirmation authorizes only the action, targets, and boundaries named in
the immediately preceding understanding check.

Ask again before proceeding when any of these change:

- A new file, directory, repository, or external system is involved.
- The proposed content or operation becomes materially different.
- The implementation needs a broader file pattern or a destructive action.
- A command introduces an unlisted generated artifact or side effect.
- The user's response is ambiguous, conditional, or does not clearly approve
  the proposed write.

Do not infer approval from silence, a topic change, or the fact that the user
originally asked for the task. When in doubt, pause and ask.

## Understanding Format
Use this concise structure:

- File action I am about to take
- Target file(s), directory(ies), or file pattern(s)
- Intended change
- Potential indirect side effects
- Boundary and assumptions
- What is still unclear, if anything
- Confirmation request

The target list may use a clearly bounded pattern such as
`src/**/*.ts`, but do not hide an unknown or unbounded scope behind a broad
pattern.

## Examples

### Direct edit

```text
File action I am about to take:
- Edit an existing Markdown file.

Target file(s):
- README.md

Intended change:
- Add installation instructions.

Potential indirect side effects:
- None expected.

Boundary and assumptions:
- I will only change the installation section.
- I will not change project behavior or other files.

What is still unclear:
- Nothing.

Please confirm before I write this file.
```

### Command with an implicit write

```text
File action I am about to take:
- Run the formatter on the selected source files.

Target file(s):
- src/**/*.ts

Intended change:
- Apply the repository formatter to existing source files.

Potential indirect side effects:
- The formatter may update generated formatting metadata or a lockfile if
  the project tooling does so.

Boundary and assumptions:
- I will not modify files outside the listed source pattern or generated
  artifacts identified before execution.

What is still unclear:
- Nothing.

Please confirm before I run the formatter.
```

### Scope change after approval

If the user approved `README.md` but implementation reveals that
`docs/install.md` must also change, stop and present a new understanding check
for the additional file. The first approval does not cover the new target.

## Common Mistakes

- Writing to disk before presenting the understanding check.
- Treating the user's initial task request as approval of an unreviewed plan.
- Listing only source files while omitting generated artifacts or metadata.
- Running a formatter, test, build, migration, or generator without checking
  whether it writes files.
- Expanding the target set after approval without asking again.
- Treating an ambiguous response as permission.
- Hiding an unknown scope behind `**/*` or another unbounded pattern.
- Treating this skill as a file-system sandbox. It is a collaboration rule;
  enforcement still depends on the agent and its tool environment.
