import numpy as np, cv2, itertools
b=cv2.imread("ros6_hi.png",cv2.IMREAD_UNCHANGED); M=(b[...,3]>128).astype(np.uint8)
S=200; ys,xs=np.nonzero(M); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max(); sc=(S*0.9)/max(x1-x0,y1-y0)
T=cv2.resize(M[y0:y1,x0:x1],(int((x1-x0)*sc),int((y1-y0)*sc)),interpolation=cv2.INTER_AREA)>0
src=open("penrose.py").read()
def polys(L):
    ns={"__name__":"x"}; exec(src.replace("L, Wd = 5.0, 1.0",f"L, Wd = {L}, 1.0"),ns); return [p for _,p in ns["POLYS"]]
def union(P,c,ang0,flip):
    pts=[]
    for k in range(6):
        a=np.radians(ang0+60*k); R=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
        for p in P:
            q=(p-c); q=q*[flip,1]; pts.append(q@R.T)
    allq=np.concatenate(pts); lo,hi=allq.min(0),allq.max(0); s=(S*0.9)/max(hi-lo)
    m=np.zeros((int((hi-lo)[1]*s)+2,int((hi-lo)[0]*s)+2),np.uint8)
    for q in pts: cv2.fillPoly(m,[np.round((q-lo)*s*8).astype(np.int32)],1,shift=3)
    return m>0
def iou(m):
    h=max(m.shape[0],T.shape[0]); w=max(m.shape[1],T.shape[1])
    A=np.zeros((h,w),bool); B=A.copy(); A[:m.shape[0],:m.shape[1]]=m; B[:T.shape[0],:T.shape[1]]=T
    return (A&B).sum()/(A|B).sum()
best=(0,)
for L in (4.0,4.5,5.0,5.5,6.0,7.0):
    P=polys(L); allp=np.concatenate(P); lo,hi=allp.min(0),allp.max(0)
    for cx in np.linspace(lo[0],hi[0],13):
        for cy in np.linspace(lo[1],hi[1],13):
            for flip in (1,-1):
                for ang0 in range(0,60,6):
                    v=iou(union(P,np.array([cx,cy]),ang0,flip))
                    if v>best[0]: best=(v,L,cx,cy,flip,ang0)
    print(L,best,flush=True)
np.save("best.npy",np.array(best[1:],dtype=float))
