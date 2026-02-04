```prompt
# Prompt: Git Pull

Fetch and merge remote changes.

## Steps

0. Save all files: VS Code command `workbench.action.files.saveAll`
1. Record current commit: `$before = git rev-parse HEAD`
2. Pull: `git pull origin main`
3. Show changes: `git log --oneline $before..HEAD`

## Output

| Item | Value |
|------|-------|
| Branch | (branch name) |
| Commits pulled | (count) |
| Result | Success / Conflict |

**Changes pulled:**
```

abc1234 feat(ch01): Add intro
def5678 fix(ch02): Fix typo

```

(If no changes: "Already up to date.")

## Error Handling

| Error | Action |
|-------|--------|
| Conflict | Manual merge, then `git add . && git commit` |
| Local changes | `git stash` first, then pull |
| Network error | Check connection, retry |
```
