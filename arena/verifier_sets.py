"""Independent set-based coverage verifier."""
from itertools import combinations
def check(v,k,t,blocks,base):
    universe=tuple(range(base,base+v))
    missing=set(combinations(universe,t))
    for block in blocks:
        missing.difference_update(combinations(sorted(block),t))
    return len(missing)
