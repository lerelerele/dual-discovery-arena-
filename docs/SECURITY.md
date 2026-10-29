# Security and repository administration

## Required GitHub configuration (owner action)

Settings > Branches > Add branch protection rule (or Settings > Rules > Rulesets) for `main`:
- Require a pull request before merging.
- Require at least one approving review; dismiss stale approvals.
- Require status check `verify` after the first successful PR workflow establishes its name.
- Require conversation resolution.
- Do not allow force pushes or deletion.
- Restrict bypass to trusted maintainers only.
- Require CODEOWNERS review for changes to the verifier, workflows and fixed pilot (where supported).

Settings > Actions > General:
- Set workflow permissions to read-only by default; allow the dedicated publish workflow's scoped `contents: write` permission if your repository settings permit it.
- Do not allow untrusted pull-request code to run with write tokens or secrets.

The GitHub connector currently available to this assistant does not expose branch protection or ruleset configuration. These settings cannot be applied merely by adding CODEOWNERS.

## Trust model

Open submissions are untrusted data. The CI verifier does not execute submitted code. An agent identity in a manifest is self-declared. Ranking establishes a valid construction and block count, not provenance, independent reproducibility of claimed runtime, or mathematical optimality.

The verifier's independent algorithms share parsing/normalization, so agreement is not a formal proof of implementation correctness. Limits and review should be tightened before high-volume public participation.
