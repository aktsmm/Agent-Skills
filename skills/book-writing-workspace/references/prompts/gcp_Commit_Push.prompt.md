```prompt
# Prompt: Commit and Push

Save files, commit, and push to remote.

## Steps

0. Save all files: VS Code command `workbench.action.files.saveAll`
1. Check status: `git branch --show-current; git config user.name; git status --short`
   - If no changes: Report "Nothing to commit" and exit
2. Stage and commit: `git add .; git commit -m "<message>"`
3. Push: `git push origin <branch>`
4. Report result

## Commit Message Format

See `.github/instructions/git/commit-format.instructions.md`

## Output

| Item | Value |
|------|-------|
| User | (git config user.name) |
| Branch | (branch name) |
| Message | (commit message) |
| Push | Success / Failed |

## Error Handling

| Error | Action |
|-------|--------|
| No changes | Report "Nothing to commit" |
| Push rejected | Run `git pull --rebase` first |
| Auth failed | Check credentials |
```
