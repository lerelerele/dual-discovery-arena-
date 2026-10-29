"""Mock-only experimental runner. No external model calls."""
import math,random
from dataclasses import dataclass,field
class BudgetExceeded(Exception):pass
@dataclass
class Budget:
    max_cost:float
    max_verifier_calls:int
    cost:float=0.0
    verifier_calls:int=0
    def charge(self,cost):
        if type(cost) not in (float,int) or not math.isfinite(cost) or cost<0:raise ValueError("invalid cost")
        if self.cost+cost>self.max_cost:raise BudgetExceeded("cost")
        self.cost+=cost
    def use_verifier(self):
        if self.verifier_calls>=self.max_verifier_calls:raise BudgetExceeded("verifier")
        self.verifier_calls+=1
    def split(self,n):
        if n<1:raise ValueError("n")
        return [Budget(self.max_cost/n,self.max_verifier_calls//n) for _ in range(n)]
@dataclass
class Candidate:
    cid:str
    author:str
    model:str
    parents:list
    blocks:list
    size:int=None
    valid:bool=None
    lineage:dict=field(default_factory=dict)
class Agent:
    name="agent"
    def propose(self,instance,visible_pool,rnd):raise NotImplementedError
def run_condition(name,agents,instance,budget,seed,exchange,verify_fn,ledger,rounds=10**9):
    v,k,t=(instance[x] for x in ("v","k","t"))
    rnd=random.Random(seed)
    pool=[];n=0
    ids=[f"{ag.name}#{i}" for i,ag in enumerate(agents,1)]
    if len(set(ids))!=len(ids):raise ValueError("duplicate agent identities")
    try:
        for turn in range(rounds):
            for ag,aid in zip(agents,ids):
                if budget.verifier_calls>=budget.max_verifier_calls:raise BudgetExceeded("verifier")
                visible=pool if exchange else [c for c in pool if set(c.lineage)=={aid}]
                view=[{"cid":c.cid,"size":c.size,"author":c.author,"model":c.model,"blocks":c.blocks} for c in visible if c.valid]
                blocks,parents,cost,transcript=ag.propose(instance,view,rnd)
                # A model call has already happened. Charge and log before validating its proposal.
                budget.charge(cost)
                ledger.append("model_call",{"condition":name,"agent_id":aid,"model":ag.name,"round":turn,"cost":cost,"transcript":transcript})
                allowed={c.cid:c for c in visible if c.valid}
                reason=None
                if not isinstance(parents,list) or any(not isinstance(p,str) for p in parents):
                    reason="invalid parent identifiers"
                elif len(parents)!=len(set(parents)) or any(pid not in allowed for pid in parents):
                    reason="invisible, duplicate or invalid parent"
                if reason is not None:
                    ledger.append("proposal_rejected",{"condition":name,"agent_id":aid,"model":ag.name,"reason":reason})
                    continue
                try:
                    budget.use_verifier()
                    result=verify_fn(v,k,t,blocks,instance.get("base",0))
                except AssertionError:
                    raise
                except (ValueError,TypeError,IndexError,OverflowError) as e:
                    ledger.append("proposal_rejected",{"condition":name,"agent_id":aid,"model":ag.name,"reason":str(e),"verifier_charged":True})
                    continue
                n+=1
                lineage={aid:{"model":ag.name,"contributions":1}}
                for pid in parents:
                    for ancestor,meta in allowed[pid].lineage.items():
                        item=lineage.setdefault(ancestor,{"model":meta["model"],"contributions":0})
                        item["contributions"]+=meta["contributions"]
                cand=Candidate(f"{name}-{n}",aid,ag.name,parents,blocks,result.get("size"),result.get("valid"),lineage)
                pool.append(cand)
                ledger.append("candidate",{"condition":name,"cid":cand.cid,"author":aid,"model":ag.name,"parents":parents,"size":cand.size,"valid":cand.valid,"lineage":lineage})
    except BudgetExceeded as e:
        ledger.append("budget_exhausted",{"condition":name,"which":str(e),"cost":budget.cost,"verifier_calls":budget.verifier_calls})
    valid=[c for c in pool if c.valid]
    best=min(valid,key=lambda c:c.size) if valid else None
    return {"condition":name,"best_size":best.size if best else None,"best_cid":best.cid if best else None,"best_lineage":best.lineage if best else None,"cost":round(budget.cost,6),"verifier_calls":budget.verifier_calls,"candidates":len(pool)}
def run_F(agents,instance,budget,seed,verify_fn,ledger):
    parts=[run_condition(f"F/{i}-{ag.name}",[ag],instance,b,seed+i,False,verify_fn,ledger) for i,(ag,b) in enumerate(zip(agents,budget.split(len(agents))))]
    ok=[p for p in parts if p["best_size"] is not None]
    best=min(ok,key=lambda p:p["best_size"]) if ok else parts[0]
    return {**best,"condition":"F","parts":parts,"cost":sum(p["cost"] for p in parts),"verifier_calls":sum(p["verifier_calls"] for p in parts)}
