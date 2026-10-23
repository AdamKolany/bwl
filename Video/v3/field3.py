import subprocess, numpy as np
S="/tmp/mb3/v3take.mp4"
W,H,FPS=960,600,4   # half resolution of the 1920x1200 frame
p=subprocess.Popen(["ffmpeg","-v","error","-ss","8.485","-i",S,"-vf",f"crop=1920:1054:0:58,pad=1920:1200:0:0:black,fps={FPS},scale={W}:{H},format=gray","-f","rawvideo","-"],stdout=subprocess.PIPE)
res=[]; i=0
while True:
    b=p.stdout.read(W*H)
    if len(b)<W*H: break
    f=np.frombuffer(b,np.uint8).reshape(H,W)
    dark=(f[:,60:780]<90).mean(axis=1)
    rows=np.where(dark>0.85)[0]
    top=int(rows[0])*2 if len(rows) else -1
    res.append((i/FPS,top)); i+=1
np.save("/tmp/mb3/field.npy",np.array(res))
prev=None
for t,y in res:
    if y!=prev: print(f"{t:7.2f}s  top={y}"); prev=y
print("frames",len(res))
