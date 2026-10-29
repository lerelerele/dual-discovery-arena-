#!/usr/bin/env python3
"""Prepare an agent submission; never needs a GitHub token."""
import argparse,json,re,shutil,sys
from pathlib import Path
from verify import load_blocks,verify

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--participant",required=True)
 p.add_argument("--id",required=True)
 p.add_argument("--v",type=int,required=True)
 p.add_argument("--k",type=int,required=True)
 p.add_argument("--t",type=int,required=True)
 p.add_argument("--base",type=int,choices=[0,1],required=True)
 p.add_argument("--blocks",type=Path,required=True)
 p.add_argument("--method",default="unspecified")
 a=p.parse_args()
 if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",a.id) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",a.participant):
  p.error("id and participant must use 1-64 alphanumeric, dash or underscore characters")
 pilot=json.loads(Path("pilot_instances.json").read_text())
 allowed={(i["v"],i["k"],i["t"]) for i in pilot["instances"]}|{(7,3,2),(12,6,4)}
 if Path("impact_instances.json").exists():
  allowed|={(i["v"],i["k"],i["t"]) for i in json.loads(Path("impact_instances.json").read_text())["instances"]}
 if (a.v,a.k,a.t) not in allowed:p.error("instance not in pilot or impact set")
 if a.blocks.stat().st_size>2000000:p.error("blocks file too large")
 check=verify(a.v,a.k,a.t,load_blocks(a.blocks),a.base)
 if not check["valid"]:p.error(f"invalid covering: {check}")
 dest=Path("submissions")/a.id
 if dest.exists():p.error("submission id already exists")
 dest.mkdir(parents=True)
 shutil.copyfile(a.blocks,dest/"blocks.txt")
 (dest/"manifest.json").write_text(json.dumps({"participant":a.participant,"condition":"open","v":a.v,"k":a.k,"t":a.t,"base":a.base,"method":a.method},indent=2)+"\n")
 print(f"Validated {check['size']} blocks; created {dest}. Commit and open a pull request.")

if __name__=="__main__":main()
