"""Independent bitmask coverage verifier (no itertools combinations)."""
from math import comb
def check(v,k,t,blocks,base):
    total=comb(v,t)
    flags=bytearray(total)
    def rank(items):
        # Combinatorial number system, colex rank.
        return sum(comb(x,j+1) for j,x in enumerate(items))
    def subsets(items,start,chosen):
        if len(chosen)==t:
            flags[rank(chosen)]=1
            return
        need=t-len(chosen)
        for i in range(start,len(items)-need+1):
            subsets(items,i+1,chosen+[items[i]])
    for block in blocks:
        subsets(sorted(x-base for x in block),0,[])
    return flags.count(0)
