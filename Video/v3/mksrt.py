# Untertitel = Blasentexte (Hand-Umbrüche zu einer Zeile), Zeiten aus v3take.srt, um das Intro verschoben
import sys
src, blasen, off, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
def t(s): h, m, r = s.split(":"); s, ms = r.split(","); return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
def f(x): ms = round(x*1000); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
M, cur = {}, None
for l in open(blasen, encoding="utf-8").read().split("\n"):
    if l.startswith("# "): continue
    if l.startswith("###"): cur = int(l.split()[1]); M[cur] = []
    elif cur is not None and l.strip(): M[cur].append(" ".join(l.split()))
o = []
for i, b in enumerate(open(src, encoding="utf-8").read().strip().split("\n\n"), 1):
    a, c = map(t, b.split("\n")[1].split(" --> "))
    o.append(f"{i}\n{f(a+off)} --> {f(c+off)}\n{' '.join(M.get(i) or b.split(chr(10))[2:])}\n")
open(out, "w", encoding="utf-8").write("\n".join(o))
