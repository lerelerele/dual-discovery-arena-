"""Mock search agents: deterministic, no provider credentials."""
from itertools import combinations
from .core import Agent
def repair(v,k,t,blocks,rnd,bias):
    covered=set()
    for b in blocks:covered.update(combinations(sorted(b),t))
    for s in combinations(range(v),t):
        if s not in covered:
            rest=[x for x in range(v) if x not in s]
            if bias=="low" and rnd.random()<0.5:extra=rest[:k-t]
            else:extra=rnd.sample(rest,k-t)
            block=sorted(s+tuple(extra));blocks.append(block);covered.update(combinations(block,t))
    return blocks
class MockAgent(Agent):
    def __init__(self,name,bias="none",cost=0.01):self.name,self.bias,self.cost=name,bias,cost
    def propose(self,instance,view,rnd):
        v,k,t=(instance[x] for x in ("v","k","t"))
        if view:
            parent=min(view,key=lambda c:c["size"])
            blocks=[list(b) for b in parent["blocks"]]
            for _ in range(rnd.randint(1,3)):
                if blocks:blocks.pop(rnd.randrange(len(blocks)))
            parents=[parent["cid"]]
        else:blocks,parents=[],[]
        return repair(v,k,t,blocks,rnd,self.bias),parents,self.cost,{"note":"mock","parents":parents}
