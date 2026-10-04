# Agents Overview

Agent steps handle judgment and MCP research. Scripts handle deterministic application.

| Role         | Responsibility                                              |
| ------------ | ----------------------------------------------------------- |
| Orchestrator | Choose mode, coordinate steps, enforce gate result          |
| Prepare      | Classify fetched updates and create initial region judgment |
| Review       | Re-check Deploy Region and official status through MCP/Docs |
| Build        | Insert Weekly / Appendix slides from manifests              |
| Notes        | Generate customer-facing speaker notes                      |
| Enrich       | Apply TOC, UPDATE Points, notes, and region stamps          |
| Finalize     | Run Verify, open the deck, and report script exit codes     |

Do not hard-code customer values in agent definitions. Use workspace config and manifests.

## Agent Registry

Moved from SKILL.md "Agent Registry".

- Skill `agents/` is the role-definition source for this workflow.
- Copy agents to workspace `.github/agents/` only when the host requires a workspace agent registry.
- Copied workspace agents are derived artifacts; do not hard-code customer values in them.
