---
name: confirm-before-work
description: Use when the assistant is about to create, edit, overwrite, or delete files on disk and must ask for confirmation first.
---

# Confirm Before Work

## Overview
Use this skill before any action that writes to a file.

## Core Rule
1. State the file action you think you are about to take.
2. List the target file(s), intended change, assumptions, boundaries, and any open question.
3. If the request is ambiguous, say what is unclear.
4. Ask for confirmation.
5. Do not create, edit, overwrite, or delete files until the user approves.

## Scope
Apply this only when the next step would modify files on disk.

Reading, searching, reasoning, and drafting in chat do not count as file writes.

If the request is unclear, keep the ambiguity explicit in the understanding check, then wait.

## Understanding Format
- File action I am about to take
- Target file(s)
- Intended change
- Boundary and assumptions
- What is still unclear, if anything
- Confirmation request

## Common Mistakes
- Writing to disk before approval.
- Treating reading or analysis as if it were a file write.
- Hiding the real request inside a long plan instead of a concise understanding check.
