# bwl-Formeleditor als Eingabe für STACK-Fragen

Machbarkeitstest (Okt. 2026): Die bwl-Bildschirmtastatur wird in STACK-Fragen eingebettet; die Eingabe
geht als Maxima-Text in das STACK-Antwortfeld, bewertet wird von STACK/Maxima. Erst Moodle, dann ILIAS.

## Aufteilung

| Ordner | Inhalt | für ILIAS |
|---|---|---|
| `gemeinsam/editor/` | Editor-Seite (aus einer echten bwl-Seite gebaut), Brücke zu STACK, LaTeX/MathJSON ↔ Maxima | unverändert |
| `gemeinsam/aufgaben/` | Export der Aufgaben aus der DB `bwl`, Umrechnung, Prüfung aller Musterlösungen mit Maxima | unverändert |
| `gemeinsam/fragen/` | erzeugt STACK-Fragen im Moodle-XML-Format (das importiert auch ILIAS' STACK-Plugin) | unverändert (ggf. Editor-URL) |
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

Danach plattformspezifisch: `moodle/README.md` bzw. `ilias/README.md`.
