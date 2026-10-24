# v03_06: Blasen-Datei und Sprecher-Spuren aus v03_05 übernehmen, neue Blöcke einsetzen, Zeiten aus der neuen Aufnahme
import sys, re, shutil, os
old_b, srt, out_b, vo_old, vo_gen, vo_new = sys.argv[1:7]
NEW = {6: "⇧ einmal tippen: nur der nächste Buchstabe wird groß.",
       7: "⇧ zweimal tippen: alle Buchstaben groß –\nbis Sie ⇧ ein drittes Mal tippen.",
       8: "⌫ löscht die Buchstaben wieder.",
       9: "Die Tasten ← → bewegen den Cursor Schritt für Schritt –\nvom Zähler in den Nenner, in die Wurzel und in den Exponenten.",
       12: "Die Taste „heraus“ springt jeweils eine Ebene hinaus:\naus dem Exponenten, aus der Wurzel, aus dem Bruch.",
       36: "Die Taste „heraus“, dann + e: e mit ◀ markieren,\ndann die Potenz-Taste mit Schrägstrich-Bruch.",
       37: "Im Exponenten: − x, → in den Nenner, dann 2.",
       38: "Einmal „heraus“ – fertig?"}
GEN = {6: 1, 7: 2, 8: 10, 9: 5, 12: 6, 36: 7, 37: 8, 38: 9}   # 10 = neu (gen/10.wav)
OLD = {**{i: i for i in range(1, 6)}, 10: 8, 11: 9, 13: 11, 14: 12, 15: 13, 16: 14, 17: 15, 18: 16,
       **{n: n - 1 for n in range(19, 36)}, **{n: n - 1 for n in range(39, 49)}}
txt = open(old_b, encoding="utf-8").read()
head = "".join(l + "\n" for l in txt.split("\n") if l.startswith("# ")) + "\n"
blocks = {}
for b in re.split(r"\n(?=### )", txt):
    if b.startswith("### "):
        l = b.strip().split("\n"); blocks[int(l[0].split()[1])] = "\n".join(l[1:])
blocks[13] = blocks[13].replace("hier am Ende.", "hier direkt dahinter.")
def ts(s): h, m, r = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(r.replace(",", "."))
def f(x): return f"{int(x // 60)}:{x % 60:05.2f}"
cues = [b.split("\n") for b in open(srt, encoding="utf-8").read().strip().split("\n\n")]
assert len(cues) == 48, len(cues)
o = [head.rstrip("\n") + "\n"]
for n, c in enumerate(cues, 1):
    a, e = (ts(x) for x in c[1].split(" --> "))
    body = NEW[n] if n in NEW else blocks[OLD[n]]
    o.append(f"### {n:02d}  {f(a)} – {f(e)}{'  (Einleitung)' if n <= 2 else ''}\n{body}\n")
open(out_b, "w", encoding="utf-8").write("\n".join(o))
os.makedirs(vo_new, exist_ok=True)
lines_old = [l.strip() for l in open(f"{vo_old}/lines.txt", encoding="utf-8") if l.strip()]
lines_gen = [l.strip() for l in open(f"{vo_gen}/lines.txt", encoding="utf-8") if l.strip()]
L = []
for n in range(1, 49):
    if n in GEN: shutil.copy(f"{vo_gen}/{GEN[n]:02d}.wav", f"{vo_new}/{n:02d}.wav"); L.append(lines_gen[GEN[n] - 1])
    else: shutil.copy(f"{vo_old}/{OLD[n]:02d}.wav", f"{vo_new}/{n:02d}.wav"); L.append(lines_old[OLD[n] - 1])
open(f"{vo_new}/lines.txt", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok")
