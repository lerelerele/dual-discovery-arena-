import json,re
from pathlib import Path
from verify import verify,load_blocks

ROOT=Path(__file__).resolve().parents[1]
pilot=json.loads((ROOT/"pilot_instances.json").read_text())
allowed={(x["v"],x["k"],x["t"]) for x in pilot["instances"]}|{(7,3,2),(12,6,4)}

def run():
    results=[]
    for p in sorted((ROOT/"submissions").glob("*/manifest.json")):
        try:
            m=json.loads(p.read_text())
            v,k,t=[m[x] for x in ("v","k","t")]
            if any(type(x) is not int for x in (v,k,t)) or (v,k,t) not in allowed: raise ValueError("instance not in pilot")
            if not re.fullmatch("[A-Za-z0-9_-]{1,64}",m["participant"]): raise ValueError("invalid participant")
            if m["condition"]!="open": raise ValueError("only open entries accepted; controlled runs require separate audit")
            path=p.parent/"blocks.txt"
            if path.is_symlink() or not path.is_file() or path.stat().st_size>2000000: raise ValueError("invalid blocks file")
            result=verify(v,k,t,load_blocks(path),m["base"])
            row={"id":p.parent.name,"participant":m["participant"],"instance":f"C({v},{k},{t})","blocks":result["size"],"valid":result["valid"]}
            if not result["valid"]: row["error"]=str(result)
        except Exception as e:
            row={"id":p.parent.name,"valid":False,"error":str(e)}
        results.append(row)
    (ROOT/"leaderboard.json").write_text(json.dumps(results,indent=2)+"\n")
    rows=sorted((r for r in results if r["valid"]),key=lambda r:(r["instance"],r["blocks"],r["participant"],r["id"]))
    lines=["# Dual Discovery Arena — Verified leaderboard","","Smaller block count is better. Entries are verified constructions, not proofs of optimality.","","| Instance | Blocks | Participant | Submission |","|---|---:|---|---|"]
    lines += [f'| {r["instance"]} | {r["blocks"]} | {r["participant"]} | {r["id"]} |' for r in rows]
    if not rows: lines.append("| — | — | No valid entries | — |")
    lines += ["",f'Rejected submissions: {sum(not r["valid"] for r in results)}.']
    (ROOT/"LEADERBOARD.md").write_text("\n".join(lines)+"\n")
    if any(not r["valid"] for r in results): raise SystemExit("invalid submission(s)")
    print(f"Verified {len(rows)} solutions")

if __name__=="__main__":run()
