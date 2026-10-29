#!/usr/bin/env python3
"""Differential test: set verifier, colex verifier, independent brute force."""
import random
import sys
from itertools import combinations
from arena.verifier_sets import check as S
from arena.verifier_bits import check as B

def oracle(v,k,t,blocks,base):
    bsets=[set(b) for b in blocks]
    return sum(1 for s in combinations(range(base,base+v),t) if not any(set(s)<=b for b in bsets))

def cases(rnd,n):
    F=[[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]]
    yield 7,3,2,F,0
    yield 7,3,2,F[:-1],0
    yield 7,3,2,[[x+1 for x in b] for b in F],1
    yield 7,3,2,F+F,0
    yield 6,6,6,[[0,1,2,3,4,5]],0
    yield 6,3,1,[[0,1,2]],0
    yield 6,3,1,[[0,1,2],[3,4,5]],0
    yield 8,4,4,[list(c) for c in combinations(range(8),4)],0
    for _ in range(n):
        v=rnd.randint(4,14)
        t=rnd.randint(1,min(5,v))
        k=rnd.randint(t,min(v,9))
        base=rnd.choice((0,1))
        blocks=[sorted(x+base for x in rnd.sample(range(v),k)) for _ in range(rnd.randint(1,80))]
        if rnd.random()<0.3:
            for b in blocks:rnd.shuffle(b)
        yield v,k,t,blocks,base

def run(n=2000,seed=12345):
    for count,(v,k,t,blocks,base) in enumerate(cases(random.Random(seed),n),1):
        a=S(v,k,t,blocks,base);b=B(v,k,t,blocks,base);c=oracle(v,k,t,blocks,base)
        if a!=b or b!=c:raise AssertionError(f"Mismatch case {count}: {a} {b} {c}")
    print(f"OK: {count} cases")

if __name__=="__main__":run(int(sys.argv[1]) if len(sys.argv)>1 else 2000)
