"""Append-only hash chain. Hashes alone do not authenticate the author."""
import hashlib,json,time
GENESIS="0"*64
def _digest(entry):
    body={k:v for k,v in entry.items() if k not in ("hash","sig")}
    return hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
class Ledger:
    def __init__(self,path,run_meta,sign_hook=None):
        self.path=path;self.prev=GENESIS;self.sign_hook=sign_hook;self.seq=0
        open(path,"x").close()
        self.append("run_start",run_meta)
    def append(self,kind,data):
        entry={"seq":self.seq,"ts":time.time(),"kind":kind,"data":data,"prev":self.prev}
        entry["hash"]=_digest(entry)
        if self.sign_hook:entry["sig"]=self.sign_hook(entry["hash"])
        with open(self.path,"a") as f:f.write(json.dumps(entry,ensure_ascii=False)+"\n")
        self.prev=entry["hash"];self.seq+=1
        return entry["hash"]
    def close(self,summary):return self.append("run_end",summary)
def verify_chain(path,verify_signature=None):
    prev=GENESIS
    with open(path) as f:
        for i,line in enumerate(f):
            e=json.loads(line)
            if e["seq"]!=i or e["prev"]!=prev or _digest(e)!=e["hash"]:return False,i
            if verify_signature is not None and (not e.get("sig") or not verify_signature(e["hash"],e["sig"])):return False,i
            prev=e["hash"]
    return True,prev
