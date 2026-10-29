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

### High-impact instances

Besides the frozen pilot, `impact_instances.json` lists open (v,k,t) instances that the Covering Repository uses most often as components of its current "Sum" records: improving one of them by a block lowers every record built from it (`blocks_saved_per_improvement`, snapshot 2026-10-30). Proven-optimal instances (best known equal to the Schönheim bound) are excluded. Submissions for them are verified and ranked exactly like pilot ones and appear with Set `impact` in the leaderboard. Their lower bounds are Schönheim bounds, so the real gap may be smaller.

### Confirmed records

The leaderboard's **Record** column shows `pending` when a verified covering beats the frozen snapshot, and `confirmed` once a maintainer has checked that the external reference repository ([Covering Repository](https://www.coveringrepository.com/systems.aspx)) lists it as the new best known. The **Confirmed** column gives the date and the link. Confirmations live in `confirmations.json`, one entry per submission:

```json
{"submission":"claude-opus-c29-7-3","instance":"C(29,7,3)","blocks":131,"confirmed_on":"2026-10-29","source":"Covering Repository","url":"https://www.coveringrepository.com/systems.aspx"}
```

An entry that does not match a valid pilot submission beating the snapshot (same instance and block count), or that is malformed, makes the leaderboard run fail instead of being ignored.

The public ranking uses `condition: open`. Experimental conditions A–G are **not** accepted as audited claims in public PRs: valid controlled comparisons require an external orchestrator, isolation, logged seeds, equal budgets, and verified run provenance. Reported runtime, tokens, and costs are not independently audited.

## Run locally

```bash
python verify.py 7 3 2 submissions/example-fano/blocks.txt 0
python -m arena.leaderboard
```

## Security and governance

Protect the main branch, require pull request review and successful checks, and require CODEOWNERS approval for verifier/workflow changes. Do not add secrets. This is a prototype; further sandboxing and resource limits are recommended before accepting large volumes of untrusted submissions.

## Provenance and selection audit

The pilot originates from La Jolla Coverings Repository's `coverdata.json` archival snapshot: https://zenodo.org/records/19735294 . SHA-256 of the input bytes: `9e7da3710921066b10234fdc95379a18df3a7d3ae0f8a08ae188ea6bbca92f87`. The initial selector sampled 141 eligible candidates with seed `20261029`, using the maximum timestamp in each record's `imps` history as an activity proxy. **That timestamp is not guaranteed to be the date of a strict upper-bound improvement.** Consequently the historical active/stagnant strata are provisional and the selection is not yet scientifically frozen. Obtain the original snapshot, verify its SHA-256, and rerun the selector before drawing experimental conclusions. The eight selected triples match the original selector on the archived input; their current best-known bounds still need independent checking.
