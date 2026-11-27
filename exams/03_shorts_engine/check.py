#!/usr/bin/env python3
"""Grader exam 03. Usage: check.py <app_dir>. Uses only ffmpeg (no ffprobe)."""
import json, os, re, subprocess, sys, hashlib, tempfile
FF="/Users/devesh/.local/bin/ffmpeg"
app=sys.argv[1]; mp4=os.path.join(app,"out","inertia.mp4"); errs=[]
def run(*a): return subprocess.run(a,capture_output=True,text=True)
if not os.path.exists(mp4): print("FAIL\nno out/inertia.mp4"); sys.exit(1)
info=run(FF,"-hide_banner","-i",mp4).stderr
m=re.search(r"Duration: (\d+):(\d+):([\d.]+)",info)
dur=int(m[1])*3600+int(m[2])*60+float(m[3]) if m else 0
if not 45<=dur<=60: errs.append(f"duration {dur:.1f}s")
if "1080x1920" not in info: errs.append("not 1080x1920")
if not re.search(r"(\d+(\.\d+)?) fps",info) or abs(float(re.search(r"(\d+(\.\d+)?) fps",info)[1])-30)>0.5: errs.append("not 30 fps")
if "Audio:" not in info or "h264" not in info: errs.append("need h264 + audio")
v=run(FF,"-hide_banner","-i",mp4,"-af","volumedetect","-vn","-f","null","-").stderr
mv=re.search(r"mean_volume: (-?[\d.]+) dB",v)
if not mv or float(mv[1])<-45: errs.append("audio silent/too quiet")
hs=set()
if dur:
    for i in range(8):
        t=dur*(i+0.5)/8
        r=subprocess.run([FF,"-v","error","-ss",str(t),"-i",mp4,"-frames:v","1","-f","image2pipe","-vcodec","png","-"],capture_output=True)
        hs.add(hashlib.md5(r.stdout).hexdigest())
    if len(hs)<8: errs.append(f"video looks static: {len(hs)}/8 distinct frames")
wp=os.path.join(app,"out","inertia.words.json")
if not os.path.exists(wp): errs.append("no words file")
else:
    w=json.load(open(wp)); ts=[x["start"] for x in w]
    if ts!=sorted(ts) or len(ts)<90: errs.append("word timestamps bad")
if not os.path.exists(os.path.join(app,"js","physics.js")): errs.append("no js/physics.js")
print("PASS (machine checks only; Devesh judges look & voice)" if not errs else "FAIL\n"+"\n".join(errs)); sys.exit(1 if errs else 0)
