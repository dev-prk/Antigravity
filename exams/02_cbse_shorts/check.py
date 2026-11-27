#!/usr/bin/env python3
"""Grader for exam 02. Usage: check.py <app_dir>  (expects content/class9_science.json)"""
import json, os, re, sys
def validate(shorts):
    errs=[]
    if len(shorts)!=10: errs.append(f"need 10 shorts, got {len(shorts)}")
    ids=[s.get("id") for s in shorts]
    if len(set(ids))!=len(ids): errs.append("duplicate ids")
    for s in shorts:
        i=s.get("id","?")
        for k in "id class subject chapter title hook narration terms scenes misconception".split():
            if k not in s or s[k] in ("",None,[]): errs.append(f"{i}: missing {k}")
        n=len(re.findall(r"\b[\w'-]+\b",s.get("narration","")))
        if not 100<=n<=130: errs.append(f"{i}: narration {n} words")
        if not 4<=len(s.get("scenes",[]))<=6: errs.append(f"{i}: scenes count")
        for t in s.get("terms",[]):
            if t.get("word","").lower() not in s.get("narration","").lower(): errs.append(f"{i}: term '{t.get('word')}' not in narration")
    txt=" ".join(s.get("narration","").lower() for s in shorts)
    if not re.search(r"different (bod|object)|two different|on each other|on different",txt): errs.append("3rd law: different-bodies not stated")
    if not re.search(r"\d+\s*(kg)?.*\d+\s*m/s",txt): errs.append("no numeric F=ma example")
    return errs
if __name__=="__main__":
    # self-test: planted bad file must fail
    bad=[{"id":"x","narration":"too short","scenes":[]}]
    assert validate(bad), "grader failed to reject bad file"
    p=os.path.join(sys.argv[1],"content","class9_science.json")
    e=validate(json.load(open(p)))
    print("PASS" if not e else "FAIL\n"+"\n".join(e)); sys.exit(1 if e else 0)
