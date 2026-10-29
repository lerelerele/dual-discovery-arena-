"""Tests for confirmations.json handling in arena.leaderboard.

Each case runs the leaderboard on a temporary copy of the repository, so the
real leaderboard files are never touched.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SID = "claude-opus-c29-7-3"
GOOD = {"submission": SID, "instance": "C(29,7,3)", "blocks": 131,
        "confirmed_on": "2026-10-29", "source": "Covering Repository",
        "url": "https://www.coveringrepository.com/systems.aspx"}


def run_with(confirmations):
    d = Path(tempfile.mkdtemp())
    try:
        for name in ("arena", "submissions", "verify.py", "pilot_instances.json"):
            src = ROOT / name
            if src.is_dir():
                shutil.copytree(src, d / name)
            else:
                shutil.copy(src, d / name)
        if confirmations is not None:
            (d / "confirmations.json").write_text(json.dumps(confirmations))
        p = subprocess.run([sys.executable, "-m", "arena.leaderboard"], cwd=d,
                           capture_output=True, text=True)
        rows = json.loads((d / "leaderboard.json").read_text()) if p.returncode == 0 else None
        md = (d / "LEADERBOARD.md").read_text() if p.returncode == 0 else ""
        return p.returncode, rows, md
    finally:
        shutil.rmtree(d)


def status(rows, sid):
    return next(r for r in rows if r["id"] == sid).get("record_status")


def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond:
        sys.exit(1)


code, rows, _ = run_with(None)
check("no confirmations file: record is pending", code == 0 and status(rows, SID) == "pending")

code, rows, md = run_with([GOOD])
check("valid confirmation: record is confirmed", code == 0 and status(rows, SID) == "confirmed")
check("confirmed row carries date, source and URL",
      next(r for r in rows if r["id"] == SID)["confirmed"] == {
          "on": "2026-10-29", "source": "Covering Repository",
          "url": "https://www.coveringrepository.com/systems.aspx"})
check("markdown shows date and link",
      "2026-10-29 · [Covering Repository](https://www.coveringrepository.com/systems.aspx)" in md)
check("a tie with the snapshot has no record status", status(rows, "grok-bot-c16-10-4") is None)

bad = {
    "wrong block count": dict(GOOD, blocks=130),
    "unknown submission": dict(GOOD, submission="does-not-exist"),
    "date not ISO": dict(GOOD, confirmed_on="29/10/2026"),
    "impossible date": dict(GOOD, confirmed_on="2026-02-30"),
    "non-https URL": dict(GOOD, url="http://www.coveringrepository.com/systems.aspx"),
    "URL with markdown characters": dict(GOOD, url="https://example.com/a)b"),
    "extra key": dict(GOOD, extra=1),
    "missing key": {k: v for k, v in GOOD.items() if k != "source"},
    "submission that does not beat the snapshot": dict(
        GOOD, submission="grok-bot-c16-10-4", instance="C(16,10,4)", blocks=18),
    "control submission": dict(GOOD, submission="example-fano", instance="C(7,3,2)", blocks=7),
}
for name, entry in bad.items():
    check(f"rejects {name}", run_with([entry])[0] != 0)
check("rejects duplicate confirmations", run_with([GOOD, GOOD])[0] != 0)
check("rejects a non-list file", run_with(GOOD)[0] != 0)
print("OK: confirmations tests")
