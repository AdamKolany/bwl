import re, sys
src, dst, off = sys.argv[1], sys.argv[2], float(sys.argv[3])
def p(s): h, m, r = s.split(":"); sec, ms = r.split(","); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def f(t): t = max(t, 0); h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s%1)*1000))%1000:03d}"
blocks = open(src, encoding="utf-8").read().strip().split("\n\n"); out = []
for b in blocks:
    i, tl, *txt = b.split("\n"); a, e = tl.split(" --> ")
    a, e = p(a)+off, p(e)+off
    if e <= 0.3: continue
    out.append(f"{len(out)+1}\n{f(a)} --> {f(e)}\n" + "\n".join(txt))
open(dst, "w", encoding="utf-8").write("\n\n".join(out) + "\n")
