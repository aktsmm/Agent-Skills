---
name: code-simplifier
description: Guide for simplifying and refining code after coding sessions. Use when cleaning up complex code, reviewing PRs for readability, or applying consistent refactoring patterns. Triggers on simplify code, refactor, clean up, code review, コード整理, リファクタ, 複雑さ削減, コードレビュー.
argument-hint: "整理したいコードや PR、気になる複雑さ"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Code Simplifier

A guide for simplifying and refining code while preserving functionality.

## When to Use

- **Refactor**, **simplify code**, **clean up**, **code review**
- After completing a coding task or writing a logical chunk of code
- Cleaning up complex PRs before review
- Refactoring code for better readability and maintainability

## Core Principles

### 1. Preserve Functionality

Change how the code does it, never what it does. Run the existing tests before and after.

### 2. Apply Project Standards

Follow the project's configured standards (CLAUDE.md, AGENTS.md, .editorconfig, linters) over personal preference.

### 3. Enhance Clarity

- Avoid nested ternary operators; prefer switch or if/else chains
- Avoid overly compact one-liners; choose clarity over brevity
- Remove comments that only restate obvious code

### 4. Maintain Balance

Avoid over-simplification that could:

- Reduce code clarity or maintainability
- Create overly clever solutions that are hard to understand
- Combine too many concerns into single functions
- Remove helpful abstractions that improve organization
- Make the code harder to debug or extend

### 5. Focus Scope

Only refine code that has been recently modified or touched, unless explicitly instructed to review a broader scope.

## Refactoring Patterns

See [references/refactoring-patterns.md](references/refactoring-patterns.md) for the pattern table, behavior-changing equivalence traps, and review feedback format.

## Done Criteria

- [ ] All tests pass after refactoring
- [ ] No functionality changed
- [ ] Code follows project standards
- [ ] No nested ternaries, overly compact one-liners, or new unnecessary abstractions
- [ ] Comments updated where logic changed
