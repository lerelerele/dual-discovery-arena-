import json,re
from pathlib import Path
from verify import verify,load_blocks
ROOT=Path(__file__).resolve().parents[1]
pilot=json.loads((ROOT/"pilot_instances.json").read_text())
records={(x["v"],x["k"],x["t"]):x for x in pilot["instances"]}
controls={(7,3,2),(12,6,4)}
def run():
    results=[]
    for p in sorted((ROOT/"submissions").glob("*/manifest.json")):
        try:
            m=json.loads(p.read_text())
            v,k,t=[m[x] for x in ("v","k","t")]
            if any(type(x) is not int for x in (v,k,t)) or (v,k,t) not in records and (v,k,t) not in controls:raise ValueError("unknown instance")
            if not re.fullmatch("[A-Za-z0-9_-]{1,64}",m["participant"]):raise ValueError("invalid participant")
            if m["condition"]!="open":raise ValueError("only open entries accepted")
            path=p.parent/"blocks.txt"
            if path.is_symlink() or not path.is_file() or path.stat().st_size>2000000:raise ValueError("invalid blocks file")
            check=verify(v,k,t,load_blocks(path),m["base"])
            row={"id":p.parent.name,"participant":m["participant"],"instance":f"C({v},{k},{t})","blocks":check["size"],"valid":check["valid"],"control":(v,k,t) in controls}
            if (v,k,t)==(12,6,4) and check["valid"] and check["size"]<41:
                raise AssertionError("CONTROL INVARIANT: C(12,6,4) below 41; investigate verifier and published bound")
            if not check["valid"]:row["error"]=str(check)
            if (v,k,t) in records:
                best=records[(v,k,t)]["best_known"]
                row.update(best_known=best,delta_to_snapshot=check["size"]-best,possible_record=check["valid"] and check["size"]<best)
        except AssertionError:
            raise
        except Exception as e:row={"id":p.parent.name,"valid":False,"error":str(e)}
        results.append(row)
    (ROOT/"leaderboard.json").write_text(json.dumps(results,indent=2)+"\n")
    valid=sorted((x for x in results if x["valid"] and not x["control"]),key=lambda x:(x["instance"],x["blocks"],x["participant"]))
    controls_valid=[x for x in results if x["valid"] and x["control"]]
    lines=["# Dual Discovery Arena — Verified leaderboard","","Smaller is better within each instance. Record flags require independent manual confirmation against current sources.","","| Instance | Blocks | Snapshot best | Delta | Possible record? | Participant | Submission |","|---|---:|---:|---:|---|---|---|"]
    for x in valid:
        lines.append(f'| {x["instance"]} | {x["blocks"]} | {x["best_known"]} | {x["delta_to_snapshot"]:+d} | {"REVIEW" if x["possible_record"] else "—"} | {x["participant"]} | {x["id"]} |')
    if not valid:lines.append("| — | — | — | — | — | No pilot submissions yet | — |")
    lines+=["","## Controls (not ranked)","","| Instance | Blocks | Participant |","|---|---:|---|"]
    for x in controls_valid:lines.append(f'| {x["instance"]} | {x["blocks"]} | {x["participant"]} |')
    lines+=["",f'Invalid or rejected entries: {sum(not x["valid"] for x in results)}.']
    (ROOT/"LEADERBOARD.md").write_text("\n".join(lines)+"\n")
    print(f"Valid pilot: {len(valid)}, controls: {len(controls_valid)}, rejected: {sum(not x['valid'] for x in results)}")
if __name__=="__main__":run()
