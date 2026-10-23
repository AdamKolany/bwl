# bwl-Formeleditor als Eingabe für STACK-Fragen

Machbarkeitstest (Okt. 2026): Die bwl-Bildschirmtastatur wird in STACK-Fragen eingebettet; die Eingabe
geht als Maxima-Text in das STACK-Antwortfeld, bewertet wird von STACK/Maxima. Erst Moodle, dann ILIAS.

## Aufteilung

| Ordner | Inhalt | für ILIAS |
|---|---|---|
| `gemeinsam/editor/` | Editor-Seite (aus einer echten bwl-Seite gebaut), Brücke zu STACK, LaTeX/MathJSON ↔ Maxima | unverändert |
| `gemeinsam/aufgaben/` | Export der Aufgaben aus der DB `bwl`, Umrechnung, Prüfung aller Musterlösungen mit Maxima | unverändert |
| `gemeinsam/fragen/` | `stackxml.js` (Fragegerüst mit Editor, Bewertung), `mkxml.js` (bwl), `mkalle.js` (Testmaterial) – Moodle-XML, das auch ILIAS' STACK-Plugin importiert | unverändert (ggf. Editor-URL) |
| `moodle/` | Import, Kurs/Tests anlegen, Fragetexte aktualisieren, Apache- und Theme-Einstellungen | nur Moodle |
| `ilias/` | Plan für den ILIAS-Test | nur ILIAS |

Wie es zusammenspielt: Fragetext → `[[iframe]]` (STACK, sandboxed) → darin `<iframe src=…/stackbwl/editor.html>`
(bwl-Tastatur) → `bridge.js` schickt Maxima per `postMessage` → Relais im Fragetext → `stack_js.request_access_to_input("ans1")`.

## Daten liegen NICHT im Repo

`answers.tsv`, `answers.json`, `bwl-stack.xml`, `vorlage.html`, `*.mac` enthalten Musterlösungen bzw. werden erzeugt.
Sie gehören in ein Arbeitsverzeichnis (auf mathe-c10-mua: `~/stackbwl`). Alle Skripte lesen/schreiben im aktuellen Verzeichnis.

## Ablauf (im Arbeitsverzeichnis, S = Pfad zu diesem Ordner)

    bash $S/gemeinsam/aufgaben/export.sh             # answers.tsv aus der DB bwl
    node $S/gemeinsam/aufgaben/conv.js               # → answers.json (LaTeX → Maxima)
    node $S/gemeinsam/aufgaben/check.js && maxima --very-quiet -b check.mac | grep '^R '   # alle 0?
    node $S/gemeinsam/aufgaben/rt.js && maxima --very-quiet -b rt.mac | grep '^R '         # alle 0?
    bash $S/gemeinsam/editor/deploy.sh               # Editor-Seite nach …/main/html/stackbwl
    node $S/gemeinsam/fragen/mkxml.js                # → bwl-stack.xml (117 STACK-Fragen)

## Verbindlich vs. Testmaterial

- **Verbindlich: DB `bwl`, Kapitel „Aufgabenauswahl“ (117 Aufgaben)** – Ablauf oben, Moodle-Kurs `bwl-STACK`.
- **Testmaterial (alt, nicht verbindlich): DBs henning, julia (abitur, drak)** – nur Formel-Aufgaben mit eindeutigem Ergebnis
  (268 Aufgaben), Moodle-Kurs `bwl-STACK-alt`. Wo die DB keine reine Endlösung hat (Vorlagen „…=“, Rechenwege),
  rechnet Maxima sie aus der Aufgabe und prüft unabhängig: Stammfunktion ableiten, bestimmte Integrale gegen
  `quad_qags`, Reihen gegen Partialsummen. Übersprungen: mehrteilige/Text-Antworten (Kurvendiskussion, Funktionen,
  Geometrie, Stochastik, Textaufgaben aus Basic …). Drei falsche DB-Lösungen (henning 15, 18, 19) werden ersetzt.

      mkdir -p alle && cd alle
      bash $S/gemeinsam/aufgaben/export_alle.sh          # all.tsv (alle DBs)
      python3 $S/gemeinsam/aufgaben/dedup.py           # Dubletten raus, ohne DB bwl → uniq.tsv
      node $S/gemeinsam/aufgaben/alle.js && maxima --very-quiet -b alle.mac > alle.out
      node $S/gemeinsam/fragen/mkalle.js                 # → bwl-stack-alle.xml

Danach plattformspezifisch: `moodle/README.md` bzw. `ilias/README.md`.
