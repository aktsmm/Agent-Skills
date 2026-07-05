# Design Rationale

goal-loop の設計根拠。SKILL.md 本体ではなく、必要時にだけ読む。

## Mechanism Mapping

- Orchestrator-workers / evaluator-optimizer: worker 生成と evaluator 判定を分け、orchestrator は state と evidence reconciliation に集中する。
- External-signal reflection: 失敗した検証出力を起点に reflection し、自己評価だけで再試行しない。
- Task / Progress ledger: frozen criteria、attempt 教訓、stall / oscillation を明示し、同じ失敗の再試行を防ぐ。
- Plan-and-Solve + Least-to-Most: 薄い全体計画を検証可能な最小サブゴールへ分解する。
- LLM-as-judge bias controls: evaluator を別 role にし、rubric と反例で position / verbosity / self-enhancement bias を抑える。
- Durable goal wrapper: 長期・多段の goal だけ durable ledger と final gate を使う。生存系機能や hidden thread state は取り込まない。

## Sources

- Anthropic, Building effective agents: https://www.anthropic.com/research/building-effective-agents
- Reflexion: https://arxiv.org/abs/2303.11366
- Self-Refine: https://arxiv.org/abs/2303.17651
- Large Language Models Cannot Self-Correct Reasoning Yet: https://arxiv.org/abs/2310.01798
- Judging LLM-as-a-Judge: https://arxiv.org/abs/2306.05685
- Magentic-One / AutoGen: https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/
- Plan-and-Solve Prompting: https://arxiv.org/abs/2305.04091
- Least-to-Most Prompting: https://arxiv.org/abs/2205.10625
- UltraGoal / oh-my-codex design reference: https://github.com/Yeachan-Heo/oh-my-codex/blob/main/docs/ultragoal.md
  - This skill is an independently written workflow inspired by UltraGoal's durable-goal, ledger, and steering concepts; it does not copy UltraGoal text or implementation.
  - oh-my-codex declares `MIT` in its package metadata: https://github.com/Yeachan-Heo/oh-my-codex/blob/main/package.json
