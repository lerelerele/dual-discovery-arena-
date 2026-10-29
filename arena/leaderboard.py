import datetime,json,re
from pathlib import Path
from verify import verify,load_blocks
ROOT=Path(__file__).resolve().parents[1]
pilot=json.loads((ROOT/"pilot_instances.json").read_text())
records={(x["v"],x["k"],x["t"]):x for x in pilot["instances"]}
controls={(7,3,2),(12,6,4)}
CONF_KEYS={"submission","instance","blocks","confirmed_on","source","url"}
def load_confirmations():
    """Maintainer-curated confirmations against the external reference repository.
    Malformed entries fail the run loudly instead of being skipped."""
    path=ROOT/"confirmations.json"
    if not path.exists():return {}
    data=json.loads(path.read_text())
    if not isinstance(data,list):raise ValueError("confirmations.json must be a JSON list")
    out={}
    for c in data:
        if not isinstance(c,dict) or set(c)!=CONF_KEYS:raise ValueError(f"confirmation entry must have exactly {sorted(CONF_KEYS)}: {c!r}")
        if not isinstance(c["submission"],str) or not re.fullmatch("[A-Za-z0-9_-]{1,64}",c["submission"]):raise ValueError(f"invalid submission id in confirmation: {c!r}")
        if not isinstance(c["instance"],str) or not re.fullmatch(r"C\(\d+,\d+,\d+\)",c["instance"]):raise ValueError(f"invalid instance in confirmation: {c!r}")
        if type(c["blocks"]) is not int or c["blocks"]<1:raise ValueError(f"invalid blocks in confirmation: {c!r}")
        if not isinstance(c["confirmed_on"],str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",c["confirmed_on"]):raise ValueError(f"confirmed_on must be YYYY-MM-DD: {c!r}")
        datetime.date.fromisoformat(c["confirmed_on"])
        if not isinstance(c["source"],str) or not re.fullmatch(r"[A-Za-z0-9 .,'-]{1,80}",c["source"]):raise ValueError(f"invalid source in confirmation: {c!r}")
        if not isinstance(c["url"],str) or not re.fullmatch(r"https://[^\s|()\[\]<>\"'`]{1,300}",c["url"]):raise ValueError(f"url must be a plain https URL: {c!r}")
        if c["submission"] in out:raise ValueError(f"duplicate confirmation for {c['submission']}")
        out[c["submission"]]=c
    return out
def run():
    confirmations=load_confirmations()
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
    # Confirmations must point at a valid pilot submission that beats the snapshot, with the same
    # instance and block count; anything else is a maintainer error and stops the run.
    by_id={x["id"]:x for x in results}
    for sid,c in confirmations.items():
        row=by_id.get(sid)
        if row is None or not row["valid"] or row["control"] or "best_known" not in row:raise ValueError(f"confirmation for {sid}: no valid pilot submission with that id")
        if c["instance"]!=row["instance"] or c["blocks"]!=row["blocks"]:raise ValueError(f"confirmation for {sid} does not match the verified submission ({row['instance']}, {row['blocks']} blocks)")
        if not row["possible_record"]:raise ValueError(f"confirmation for {sid}: submission does not beat the frozen snapshot")
        row["confirmed"]={"on":c["confirmed_on"],"source":c["source"],"url":c["url"]}
    for row in results:
        if row["valid"] and "best_known" in row:
            row["record_status"]="confirmed" if "confirmed" in row else ("pending" if row["possible_record"] else None)
    (ROOT/"leaderboard.json").write_text(json.dumps(results,indent=2)+"\n")
    valid=sorted((x for x in results if x["valid"] and not x["control"]),key=lambda x:(x["instance"],x["blocks"],x["participant"]))
    controls_valid=[x for x in results if x["valid"] and x["control"]]
    lines=["# Dual Discovery Arena — Verified leaderboard","",
           "Smaller is better within each instance. **Record**: `pending` = beats the frozen snapshot but not yet confirmed against the external reference repository; `confirmed` = a maintainer checked that the reference repository lists it as the new best known (date and link under **Confirmed**, source of truth `confirmations.json`).","",
           "| Instance | Blocks | Snapshot best | Delta | Record | Confirmed | Participant | Submission |","|---|---:|---:|---:|---|---|---|---|"]
    for x in valid:
        conf=x.get("confirmed")
        confirmed=f'{conf["on"]} · [{conf["source"]}]({conf["url"]})' if conf else "—"
        lines.append(f'| {x["instance"]} | {x["blocks"]} | {x["best_known"]} | {x["delta_to_snapshot"]:+d} | {x["record_status"] or "—"} | {confirmed} | {x["participant"]} | {x["id"]} |')
    if not valid:lines.append("| — | — | — | — | — | — | No pilot submissions yet | — |")
    lines+=["","## Controls (not ranked)","","| Instance | Blocks | Participant |","|---|---:|---|"]
    for x in controls_valid:lines.append(f'| {x["instance"]} | {x["blocks"]} | {x["participant"]} |')
    lines+=["",f'Invalid or rejected entries: {sum(not x["valid"] for x in results)}.']
    (ROOT/"LEADERBOARD.md").write_text("\n".join(lines)+"\n")
    print(f"Valid pilot: {len(valid)}, controls: {len(controls_valid)}, confirmed: {len(confirmations)}, rejected: {sum(not x['valid'] for x in results)}")
if __name__=="__main__":run()
