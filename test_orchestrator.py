"""Offline regression tests for mock orchestrator."""
import json,os,tempfile
from orchestrator.core import Budget,run_condition,run_F,Agent
from orchestrator.ledger import Ledger,verify_chain
from orchestrator.mock_agents import MockAgent
from verify import verify
INST={"v":12,"k":6,"t":4,"base":0}
def main():
    with tempfile.TemporaryDirectory() as d:
        path=os.path.join(d,"run.jsonl")
        ledger=Ledger(path,{"instance":INST,"seed":1})
        a,b=MockAgent("gpt"),MockAgent("opus","low")
        E=run_condition("E",[a,b],INST,Budget(1,30),1,True,verify,ledger)
        assert E["verifier_calls"]==30
        C=run_condition("A-cost",[a],INST,Budget(.05,1000),2,True,verify,ledger)
        assert C["cost"]<=.05+1e-9
        assert E["best_size"]>=41
        F=run_F([a,b],INST,Budget(1,30),1,verify,ledger)
        assert F["verifier_calls"]<=30
        same=run_condition("C",[MockAgent("gpt"),MockAgent("gpt")],INST,Budget(.2,10),4,True,verify,ledger)
        assert same["verifier_calls"]==10
        class InvalidParent(Agent):
            name="bad"
            def propose(self,instance,view,rnd):
                return [],["invisible-id"],.02,{"note":"invalid parent"}
        rejected=run_condition("reject",[InvalidParent()],INST,Budget(.1,3),5,False,verify,ledger,rounds=2)
        assert rejected["cost"]==.04 and rejected["verifier_calls"]==0
        ledger.close({"E":E["best_size"],"F":F["best_size"]})
        entries=[json.loads(line) for line in open(path)]
        fc=[e["data"] for e in entries if e["kind"]=="candidate" and e["data"]["condition"].startswith("F/")]
        assert all(set(c["lineage"])=={c["author"]} for c in fc)
        ec=[e["data"] for e in entries if e["kind"]=="candidate" and e["data"]["condition"]=="E"]
        assert any({m["model"] for m in c["lineage"].values()}=={"gpt","opus"} for c in ec)
        cc=[e["data"] for e in entries if e["kind"]=="candidate" and e["data"]["condition"]=="C"]
        assert {c["author"] for c in cc}=={"gpt#1","gpt#2"}
        assert any({"gpt#1","gpt#2"} <= set(c["lineage"]) for c in cc)
        rr=[e["data"] for e in entries if e["kind"]=="proposal_rejected" and e["data"]["condition"]=="reject"]
        assert len(rr)==2 and all("parent" in x["reason"] for x in rr)
        assert verify_chain(path)[0]
        lines=open(path).read().splitlines()
        altered=json.loads(lines[3]);altered["data"]["cost"]=0
        lines[3]=json.dumps(altered)
        tampered=path+".tampered"
        open(tampered,"w").write("\n".join(lines)+"\n")
        assert verify_chain(tampered)==(False,3)
        try:Ledger(path,{})
        except FileExistsError:pass
        else:raise AssertionError("ledger overwritten")
        print("OK: mock orchestrator budget, isolation, lineage and ledger tests (PR refresh)")
if __name__=="__main__":main()
