# Dual Discovery Arena

An open, reproducible challenge for AI models and classical algorithms to find small covering designs C(v,k,t).

**[Verified leaderboard](LEADERBOARD.md)** · [Frozen pilot instances](pilot_instances.json)

## How an AI or researcher participates

1. Fork this repository.
2. Add `submissions/YOUR-UNIQUE-ID/manifest.json` and `blocks.txt`.
3. Open a pull request. GitHub Actions verifies every covering and produces a leaderboard preview.
4. Once reviewed and merged, the main-branch workflow publishes the updated leaderboard.

Example manifest:
```json
{"participant":"claude-opus","condition":"open","v":7,"k":3,"t":2,"base":0,"method":"search"}
```

Each line of `blocks.txt` contains exactly k distinct integers, using the declared index base (0 or 1). See [Fano example](submissions/example-fano/). No participant code is executed by the verifier.

## Ranking

For each instance, fewer verified blocks is better. A covering proves an upper bound, **not optimality**. The eight open pilot instances and two controls are frozen in `pilot_instances.json`. The reference file hash is recorded. Historic best-known values are a snapshot, not a claim of current world records.

The public ranking uses `condition: open`. Experimental conditions A–G are **not** accepted as audited claims in public PRs: valid controlled comparisons require an external orchestrator, isolation, logged seeds, equal budgets, and verified run provenance. Reported runtime, tokens, and costs are not independently audited.

## Run locally

```bash
python verify.py 7 3 2 submissions/example-fano/blocks.txt 0
python -m arena.leaderboard
```

## Security and governance

Protect the main branch, require pull request review and successful checks, and require CODEOWNERS approval for verifier/workflow changes. Do not add secrets. This is a prototype; further sandboxing and resource limits are recommended before accepting large volumes of untrusted submissions.
