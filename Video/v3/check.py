# Prüft jede gesprochene Zeile mit Whisper; meldet Zeilen, deren Transkript zu stark abweicht.
# Mit Kandidaten (NNcK.wav) wird der beste Kandidat als NN.wav übernommen.
import sys, os, re, glob, shutil, difflib
from faster_whisper import WhisperModel
V = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else "check"
lines = [l.strip() for l in open(os.path.join(V, "lines.txt"), encoding="utf-8") if l.strip()]
norm = lambda s: re.sub(r"[^a-zäöüß0-9 ]", "", s.lower().replace("-", " ")).split()
m = WhisperModel("small", device="cpu", compute_type="int8")
def score(path, ref):
    segs, _ = m.transcribe(path, language="de", beam_size=5)
    hyp = " ".join(s.text for s in segs)
    return difflib.SequenceMatcher(None, norm(ref), norm(hyp)).ratio(), hyp.strip()
if mode == "check":
    bad = []
    for i, ref in enumerate(lines, 1):
        r, hyp = score(os.path.join(V, f"{i:02d}.wav"), ref)
        flag = r < 0.8
        if flag: bad.append(i)
        print(f"{i:2d} {r:.2f} {'BAD ' if flag else ''}{hyp}", flush=True)
    print("BAD", ",".join(map(str, bad)))
else:   # pick: beste Kandidaten übernehmen
    for i in map(int, sys.argv[3].split(",")):
        cands = sorted(glob.glob(os.path.join(V, f"{i:02d}c[0-9].wav")))
        res = [(score(c, lines[i - 1])[0], c) for c in cands]
        r, best = max(res); shutil.copy(best, os.path.join(V, f"{i:02d}.wav"))
        print(i, f"{r:.2f}", os.path.basename(best), [f"{x:.2f}" for x, _ in res], flush=True)
