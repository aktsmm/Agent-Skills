# Customization Routing

Use this guide before recommending a skill.

## Decide Whether the User Needs a Skill

| User Intent                          | Best Fit        |
| ------------------------------------ | --------------- |
| "いつもこのルールで動いて"           | Instruction     |
| "この slash task を作りたい"         | Prompt or Skill |
| "専用 persona で動かしたい"          | Agent           |
| "危険コマンドを止めたい"             | Hook            |
| "再利用できる workflow を配布したい" | Skill           |

## Fast Rules

- If the user asks for a reusable package with references, scripts, or templates, recommend a skill.
- If the user only needs a focused slash command, recommend a prompt first.
- If the user mainly needs role boundaries or tool restrictions, recommend an agent.
- If the user wants behavior enforced automatically, recommend a hook.

## Response Pattern

When the ask is not best served by a skill, say so before searching.

```markdown
This sounds closer to an instruction than a skill because the behavior should apply automatically.

Do you want:

1. An instruction template?
2. Skills anyway?
```

If the user still wants skills, continue the skill search normally.

## Recommendation Heuristics

When multiple skills match, prefer:

1. Official or curated source
2. Clear description with trigger conditions
3. Good resource structure (`scripts/`, `references/`, `assets/`)
4. Recently maintained index entries

## Collection Management

When deciding whether a discovered skill belongs in a shared collection, classify it first:

| State     | Meaning                               | Action                                                      |
| --------- | ------------------------------------- | ----------------------------------------------------------- |
| Candidate | Interesting but unproven              | Keep in a sandbox/source list; do not present as default    |
| Adopted   | Used successfully on real tasks       | Star it or install locally for repeat use                   |
| Shared    | Useful across people/repos            | Add to the maintained index or private marketplace source   |
| Retire    | Duplicate, stale, or under-triggering | Remove from recommendations or replace with a better source |

Promotion should be based on observed usage, clear trigger fit, and maintainability rather than novelty.

Source inspiration: Anthropic, "Lessons from building Claude Code: how we use skills" - https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills
