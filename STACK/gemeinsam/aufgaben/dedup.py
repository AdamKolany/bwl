# all.tsv (export_alle.sh) → uniq.tsv: Dubletten (gleicher Aufgabentext + gleiche Antwort) entfernen, DB bwl auslassen (eigener Ablauf)
rows = [l.rstrip("\n").split("\t") for l in open("all.tsv", encoding="utf-8") if l.strip()]
seen = {}
for r in rows: seen.setdefault((r[7].strip(), r[5].strip()), r)
out = [r for r in seen.values() if r[0] != "bwl"]
open("uniq.tsv", "w", encoding="utf-8").write("".join("\t".join(r) + "\n" for r in out))
print(len(rows), "Zeilen →", len(out), "eindeutige Aufgaben (ohne bwl)")
