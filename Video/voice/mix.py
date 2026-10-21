import sys, subprocess, glob, os, numpy as np, soundfile as sf
V, srt, out = sys.argv[1], sys.argv[2], sys.argv[3]
def t(s): h,m,r=s.split(":"); s,ms=r.split(","); return int(h)*3600+int(m)*60+int(s)+int(ms)/1000
cues=[]
for b in open(srt,encoding="utf-8").read().strip().split("\n\n"):
    a,c=b.split("\n")[1].split(" --> "); cues.append((t(a),t(c)))
sr=24000; total=cues[-1][1]+6
mix=np.zeros(int(total*sr),dtype=np.float32)
for i,(a,c) in enumerate(cues,1):
    p=f"{V}/{i:02d}.wav"; w,_=sf.read(p,dtype="float32")
    # trim silence
    nz=np.where(np.abs(w)>0.01)[0]; w=w[max(0,nz[0]-240):nz[-1]+2400]
    avail=c-a-0.4; d=len(w)/sr; f=1.0
    if d>avail:
        f=min(d/avail,1.3)
        q=f"{V}/{i:02d}f.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",p,"-af",f"silenceremove=start_periods=1:start_threshold=-40dB,areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse,atempo={f:.3f}",q],check=True)
        w,_=sf.read(q,dtype="float32")
    s=int((a+0.25)*sr); mix[s:s+len(w)]+=w[:len(mix)-s]
    print(f"{i:2d} cue {c-a:5.2f}s  voice {d:5.2f}s  tempo {f:.2f}{'  OVER' if len(w)/sr>c-a else ''}")
mix/=max(1,np.abs(mix).max()/0.95)
sf.write(out,mix,sr)
