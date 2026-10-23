# Stimme nach Untertitel-Zeiten platzieren – ohne Beschleunigung; wenn ein Satz länger ist als seine Blase,
# beginnt der nächste erst nach einer kurzen Pause (leichter Versatz statt gehetztem Sprechen).
import sys, numpy as np, soundfile as sf
V, srt, out = sys.argv[1], sys.argv[2], sys.argv[3]
def t(s): h, m, r = s.split(":"); s, ms = r.split(","); return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
cues = [tuple(map(t, b.split("\n")[1].split(" --> "))) for b in open(srt, encoding="utf-8").read().strip().split("\n\n")]
sr = 24000; mix = np.zeros(int((cues[-1][1] + 10) * sr), np.float32); prev = 0.0
for i, (a, c) in enumerate(cues, 1):
    w, _ = sf.read(f"{V}/{i:02d}.wav", dtype="float32")
    nz = np.nonzero(np.abs(w) > 0.01)[0]; w = w[max(0, nz[0] - 240): nz[-1] + 2400]
    st = max(a + 0.25, prev + 0.35); s = int(st * sr); mix[s:s + len(w)] += w; prev = st + len(w) / sr
    print(f"{i:2d} cue {a:7.2f}-{c:7.2f}  voice {st:7.2f}-{prev:7.2f}{'  +%.2fs' % (prev - c) if prev > c else ''}")
sf.write(out, mix[:int((prev + 0.5) * sr)], sr)
