"""Append-only hash chain. Hashes alone do not authenticate the author."""
import hashlib,json,time
GENESIS="0"*64
def _digest(entry):
    body={k:v for k,v in entry.items() if k not in ("hash","sig")}
    return hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
class Ledger:
    def __init__(self,path,run_meta,sign_hook=None):
        self.path=path;self.prev=GENESIS;self.sign_hook=sign_hook
        open(path,"x").close()
        self.append("run_start",run_meta)
    def append(self,kind,data):
        with open(self.path) as f:seq=sum(1 for _ in f)
        entry={"seq":seq,"ts":time.time(),"kind":kind,"data":data,"prev":self.prev}
        entry["hash"]=_digest(entry)
        if self.sign_hook:entry["sig"]=self.sign_hook(entry["hash"])
        with open(self.path,"a") as f:f.write(json.dumps(entry,ensure_ascii=False)+"\n")
        self.prev=entry["hash"]
        return entry["hash"]
    def close(self,summary):return self.append("run_end",summary)
def verify_chain(path):
    prev=GENESIS
    with open(path) as f:
        for i,line in enumerate(f):
            e=json.loads(line)
            if e["seq"]!=i or e["prev"]!=prev or _digest(e)!=e["hash"]:return False,i
            prev=e["hash"]
    return True,prev
