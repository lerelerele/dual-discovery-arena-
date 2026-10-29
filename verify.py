import itertools
import math
from pathlib import Path

def load_blocks(path):
    return [[int(x) for x in line.split()] for line in Path(path).read_text().splitlines() if line.strip()]

def verify(v,k,t,blocks,base):
    if type(base) is not int or base not in (0,1):
        raise ValueError("base must be explicitly 0 or 1")
    if not (0 <= t <= k <= v <= 40):
        raise ValueError("invalid parameters")
    universe=set(range(base,base+v))
    blocks=list(blocks)
    if len(blocks)>100000:
        raise ValueError("too many blocks")
    for b in blocks:
        if len(b)!=k or len(set(b))!=k or not set(b)<=universe:
            return {"valid":False,"size":len(blocks),"error":"invalid block"}
    # Two independent coverage representations.
    expected=set(itertools.combinations(sorted(universe),t))
    covered=set()
    for b in blocks:
        covered.update(itertools.combinations(sorted(b),t))
    missing_set=len(expected-covered)
    index={c:i for i,c in enumerate(itertools.combinations(sorted(universe),t))}
    bits=bytearray(len(index))
    for b in blocks:
        for c in itertools.combinations(sorted(b),t):
            bits[index[c]]=1
    missing_bitmap=bits.count(0)
    if missing_set!=missing_bitmap:
        raise AssertionError("verifiers disagree")
    return {"valid":missing_set==0,"size":len(blocks),"missing_tsets":missing_set}

if __name__=="__main__":
    import sys,json
    v,k,t=map(int,sys.argv[1:4])
    print(json.dumps(verify(v,k,t,load_blocks(sys.argv[4]),int(sys.argv[5]))))
