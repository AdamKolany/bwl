# ILIAS – noch offen

Der gemeinsame Teil ist plattformneutral: dieselbe Editor-Seite, dieselbe `bwl-stack.xml`.
Ob es in ILIAS geht, hängt an einer Frage: **unterstützt das ILIAS-STACK-Plugin (assStackQuestion) `[[iframe]]` und `stack_js`?**
(Kommt mit STACK ≥ 4.4 in den Kern; das ILIAS-Plugin portiert den STACK-Kern mit Verzögerung.)

## Schritte

1. ILIAS (Testinstanz) + STACK-Plugin installieren; Maxima-Anbindung wie in Moodle (oder goemaxima).
2. Versionsstand des Plugins prüfen: `[[iframe]]`, `[[cors]]`, `corsscripts/stackjsiframe.js` vorhanden?
3. `bwl-stack.xml` importieren (Plugin kann Moodle-XML von STACK-Fragen importieren).
4. Editor-URL: liegt ILIAS auf einem anderen Host, `STACKBWL_EDITOR=…/stackbwl/editor.html node …/mkxml.js` und
   CORS-Header für /js, /css, /stackbwl wie in `moodle/apache-moodle.conf` (Ursprung "null" der Sandbox).
5. Darstellung (Breite, Schrift) entspricht `moodle/theme-boost.scss` – in ILIAS über ein eigenes Skin/CSS.

Falls das Plugin kein `stack_js` kann: Plan B wäre ein globales Skript (Skin/Plugin), das sich an alle STACK-Eingabefelder hängt.
