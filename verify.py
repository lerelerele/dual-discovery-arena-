"""Validate covering designs with independently implemented set and colex-bitset algorithms."""
from pathlib import Path
from math import comb
from arena.verifier_sets import check as set_check
from arena.verifier_bits import check as bit_check

def load_blocks(path):
    return [[int(x) for x in line.split()] for line in Path(path).read_text().splitlines() if line.strip()]

def verify(v,k,t,blocks,base):
    if type(base) is not int or base not in (0,1):raise ValueError("base must be 0 or 1")
    if any(type(x) is not int for x in (v,k,t)) or not (1<=t<=k<=v<=40):raise ValueError("invalid parameters")
    if comb(v,t)>200000:raise ValueError("instance too large")
    blocks=list(blocks)
    if len(blocks)>100000:raise ValueError("too many blocks")
    allowed=set(range(base,base+v))
    for b in blocks:
        if len(b)!=k or len(set(b))!=k or not set(b)<=allowed:
            return {"valid":False,"size":len(blocks),"error":"invalid block"}
    a=set_check(v,k,t,blocks,base)
    b=bit_check(v,k,t,blocks,base)
    if a!=b:raise AssertionError(f"independent verifiers disagree: {a} vs {b}")
    return {"valid":a==0,"size":len(blocks),"missing_tsets":a}

if __name__=="__main__":
    import sys,json
    v,k,t=map(int,sys.argv[1:4])
    print(json.dumps(verify(v,k,t,load_blocks(sys.argv[4]),int(sys.argv[5]))))
