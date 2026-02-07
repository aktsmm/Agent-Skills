```prompt
# Prompt: Commit

Save unsaved files and create a git commit.

## Steps

0. Save all files: VS Code command `workbench.action.files.saveAll`
1. Check status: `git branch --show-current; git config user.name; git status --short`
   - If no changes: Report "Nothing to commit" and exit
2. Stage and commit: `git add .; git commit -m "<message>"`
3. Report result with commit info

## Commit Message Format

See `.github/instructions/git/commit-format.instructions.md`

Format: `<type>(<scope>): <subject>`

Examples:
- `feat(ch01): Add introduction section`
- `fix(ch03): Correct typo in terminology`
- `docs(agents): Update writing agent`

## Output

After commit, display:

| Item | Value |
|------|-------|
| User | (git config user.name) |
| Branch | (current branch) |
| Message | (commit message) |
| Files | (number of files changed) |

## Error Handling

| Error | Action |
|-------|--------|
| No changes | Report "Nothing to commit" |
| Staging failed | Check file paths |
| Commit failed | Check git status |
```
