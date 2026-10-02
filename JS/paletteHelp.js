/* paletteHelp.js — Hilfetexte zu den Tasten der Bildschirmtastatur.
 *
 * Maus:   kurz über einer Taste stehen bleiben  -> Hilfetext erscheint.
 * Touch:  Taste etwas länger gedrückt halten    -> Hilfetext erscheint,
 *         die Taste wird dabei NICHT ausgelöst.
 *
 * ==> Texte ändern/ergänzen: nur die Tabelle PALETTE_HELP unten.
 *     Schlüssel = genau der Wert von data-ins der Taste (wie er im HTML
 *     steht, also z. B. "\\mathbb{N}" für \mathbb{N} – in JS wird jeder
 *     Backslash verdoppelt), bzw. "cmd:<name>" für Tasten mit data-cmd.
 *     Tasten ohne Eintrag zeigen einfach keinen Hilfetext.
 *     Fehlende Einträge: Seite mit ?helpdebug=1 öffnen, dann stehen sie in
 *     der Browser-Konsole.
 */
(function () {
  "use strict";

  const PALETTE_HELP = {
    // --- Bearbeiten / Cursor ---------------------------------------------
    "cmd:copy":      "Auswahl kopieren",
    "cmd:paste":     "Einfügen",
    "cmd:move_L":    "Cursor nach links (auch aus Exponent, Bruch, Klammer heraus)",
    "cmd:move_R":    "Cursor nach rechts (auch aus Exponent, Bruch, Klammer heraus)",
    "cmd:exitCtx":   "Heraus: eine Ebene hinaus — Cursor hinter das innerste Konstrukt (Exponent, Bruchteil, Wurzel, Klammer …)",
    "cmd:bs":        "Zeichen links vom Cursor löschen",
    "cmd:del":       "Zeichen rechts vom Cursor löschen",
    "cmd:clear":     "Auswahl löschen",
    "cmd:selL":      "Auswahl nach links erweitern",
    "cmd:selR":      "Auswahl nach rechts erweitern",
    "cmd:selectAll": "Alles auswählen",
    "cmd:undo":      "Rückgängig",
    "cmd:redo":      "Wiederholen",
    "cmd:capsel":    "Groß-/Kleinschreibung der Auswahl umschalten",
    "cmd:capsCycle": "Großbuchstaben: einmal / dauerhaft / aus",

    // --- Rechenzeichen ---------------------------------------------------
    "=":  "Gleichheitszeichen",
    "+":  "Plus",
    "-":  "Minus",
    "·":  "Mal (Multiplikationspunkt)",
    "/":  "Geteilt",
    "\\times": "Kreuz (Kreuzprodukt / mal)",
    "\\pm": "Plus-Minus",
    "\\approx": "ungefähr gleich",
    "\\ne": "ungleich",
    "<":  "kleiner als",
    ">":  "größer als",
    "\\leqslant": "kleiner oder gleich",
    "\\geqslant": "größer oder gleich",

    // --- Brüche, Potenzen, Wurzeln, Indizes ------------------------------
    "\\frac{#0}{{#?}}":   "Bruch (Zähler / Nenner)",
    "#0^2":               "Quadrat (hoch 2)",
    "#0^3":               "hoch 3",
    "#0^{#?}":            "Potenz: hoch beliebigen Exponenten",
    "#0^{{#?}/{#?}}":     "Potenz mit Bruch im Exponenten",
    "{{}^2}":             "hoch 2 (an den vorhergehenden Ausdruck)",
    "{{}^3}":             "hoch 3 (an den vorhergehenden Ausdruck)",
    "{{}^{#?}}":          "Exponent an den vorhergehenden Ausdruck",
    "{{}^{{#?}/{#?}}}":   "Bruch-Exponent an den vorhergehenden Ausdruck",
    "\\sqrt[2]{#0}":      "Quadratwurzel",
    "\\sqrt[3]{#0}":      "dritte Wurzel",
    "\\sqrt[#?]{#0}":     "n-te Wurzel",
    "#0_{#?}":            "Index (tiefgestellt)",
    "\\overline{#0}":     "Überstrich",
    "\\hat{#0}":          "Dach (z. B. Schätzwert)",
    "#0^\\top":           "transponiert",
    "#0^\\ast":           "Stern (hochgestellt)",
    "#0!":                "Fakultät",
    "\\binom{#0}{#?}":    "Binomialkoeffizient (n über k)",

    // --- Beträge, Klammern -----------------------------------------------
    "\\left|#0\\right|":  "Betrag |…|",
    "\\big|":             "senkrechter Strich (einzeln)",
    "\\big\\|":           "Doppelstrich (einzeln)",
    "\\big(#?\\,\\big|\\,#0\\big)": "Klammer mit senkrechtem Strich (…|…) – keine normale Klammer!",
    "\\left\\langle#0\\,{,}\\,#?\\right\\rangle": "spitze Klammern ⟨…,…⟩ (Skalarprodukt)",
    "\\left(#0\\right)":  "runde Klammern (…)",
    "\\left[#0\\right]":  "eckige Klammern […]",
    "\\left\\{#0\\right\\}": "geschweifte Klammern {…} (Menge)",
    "\\left\\{#0:\\,#?\\right\\}": "Menge {… : Bedingung}",
    "\\left(#0\\,,\\;#?\\right)": "offenes Intervall (a, b)",
    "\\left[#0\\,,\\;#?\\right]": "abgeschlossenes Intervall [a, b]",
    "\\left[#0\\,,\\;#?\\right)": "halboffenes Intervall [a, b)",
    "\\left(#0\\,,\\;#?\\right]": "halboffenes Intervall (a, b]",

    // --- Mengen ----------------------------------------------------------
    "\\subseteq":   "Teilmenge",
    "\\subsetneq":  "echte Teilmenge",
    "\\cup":        "Vereinigung",
    "\\cap":        "Durchschnitt",
    "\\setminus":   "Differenz (ohne)",
    "\\in":         "Element von",
    "\\notin":      "nicht Element von",
    "\\varnothing": "leere Menge",
    "\\bigcup":     "Vereinigung über mehrere Mengen",
    "\\bigcap":     "Durchschnitt über mehrere Mengen",
    "\\mathbb{N}":  "natürliche Zahlen",
    "\\mathbb{Z}":  "ganze Zahlen",
    "\\mathbb{Q}":  "rationale Zahlen",
    "\\mathbb{R}":  "reelle Zahlen",
    "\\mathbb{C}":  "komplexe Zahlen",

    // --- Funktionen, Abbildungen -----------------------------------------
    "\\mathbf{Dm}\\left(#0\\right)": "Definitionsbereich",
    "\\mathbf{Rg}\\left(#0\\right)": "Wertebereich",
    "\\left((#0,#0)\\mapsto#?\\right)": "Zuordnung ↦ (x wird abgebildet auf …)",
    "\\xrightarrow[#0\\to#?]{}": "Pfeil mit Grenzübergang (z. B. n → ∞)",
    "\\sin\\left(#0\\right)":    "Sinus",
    "\\cos\\left(#0\\right)":    "Kosinus",
    "\\tan\\left(#0\\right)":    "Tangens",
    "\\arcsin\\left(#0\\right)": "Arkussinus",
    "\\arccos\\left(#0\\right)": "Arkuskosinus",
    "\\arctan\\left(#0\\right)": "Arkustangens",
    "\\exp\\left(#0\\right)":    "Exponentialfunktion exp(…)",
    "\\ln\\left(#0\\right)":     "natürlicher Logarithmus",
    "\\log\\left(#0\\right)":    "Logarithmus",
    "\\lim\\limits_{n\\to\\infty}": "Grenzwert für n → ∞",
    "\\int":        "Integral",
    "\\,\\text{d}": "Differential d (z. B. dx beim Integral)",
    "\\sum":        "Summe",

    // --- Logik -----------------------------------------------------------
    "\\forall":         "für alle",
    "\\exists":         "es gibt",
    "\\neg":            "nicht",
    "\\vee":            "oder",
    "\\wedge":          "und",
    "\\Rightarrow":     "daraus folgt",
    "\\Leftrightarrow": "genau dann, wenn (äquivalent)",
    "\\leftrightarrow": "Doppelpfeil",

    // --- Konstanten, griechische Buchstaben ------------------------------
    "\\pi":         "Kreiszahl π",
    "\\mathbf{e}":  "Eulersche Zahl e",
    "\\imath":      "imaginäre Einheit i",
    "\\infty":      "unendlich",
    "\\alpha":      "alpha",
    "\\beta":       "beta",
    "\\gamma":      "gamma",
    "\\varepsilon": "epsilon",
    "\\lambda":     "lambda",
    "\\mu":         "mü",
    "\\sigma":      "sigma",
    "\\tau":        "tau",
    "\\chi^2":      "Chi-Quadrat",
    "\\Delta":      "Delta (groß)",
    "\\Phi":        "Phi (groß)",
    "\\Omega":      "Omega (groß)",
    "\\bullet":     "Punkt (fett)",
    "\\circ":       "Kringel (z. B. Verkettung f∘g)",

    // --- Sonstiges -------------------------------------------------------
    "\\euro":  "Euro",
    "\\%":     "Prozent",
    "‰":       "Promille",
    "\\ldots": "Pünktchen …",
    "'":       "Strich (Ableitung f')",
    ".":       "Punkt",
    "{,}":     "Dezimalkomma",
    ";":       "Semikolon",
    "\\,":     "kleiner Abstand"
  };

  const HOVER_MS = 600;   // Maus: Verweilzeit bis zum Hilfetext
  const PRESS_MS = 500;   // Touch: Haltezeit bis zum Hilfetext
  const SHOW_MS  = 2500;  // Touch: so lange bleibt der Text nach dem Loslassen

  function keyOf(btn) {
    const cmd = btn.getAttribute("data-cmd");
    return cmd ? "cmd:" + cmd : (btn.getAttribute("data-ins") || "");
  }
  function helpOf(btn) { return PALETTE_HELP[keyOf(btn)] || ""; }

  const style = document.createElement("style");
  style.textContent =
    "#pbtnHelp{position:fixed;z-index:9999;pointer-events:none;max-width:18em;" +
    "padding:.3em .6em;border-radius:6px;background:#333;color:#fff;font:14px/1.3 sans-serif;" +
    "box-shadow:0 2px 6px rgba(0,0,0,.3);opacity:0;transition:opacity .12s;}" +
    "#pbtnHelp.on{opacity:1;}" +
    // Langes Drücken (Hilfe-Tooltip) startete auf dem iPad die native
    // Textauswahl der Seite (blauer Balken über eine ganze Tastenzeile).
    ".palette,.palette *,.pbtn{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none;}";
  document.head.appendChild(style);

  let tip = null, timer = null, hideTimer = null, suppressClick = false, start = null;

  function show(btn) {
    const txt = helpOf(btn); if (!txt) return false;
    if (!tip) { tip = document.createElement("div"); tip.id = "pbtnHelp"; document.body.appendChild(tip); }
    tip.textContent = txt;
    const r = btn.getBoundingClientRect();
    tip.style.left = "0px"; tip.style.top = "0px"; tip.classList.add("on");
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = r.left + r.width / 2 - w / 2;
    x = Math.max(4, Math.min(x, window.innerWidth - w - 4));
    let y = r.top - h - 6; if (y < 4) y = r.bottom + 6;
    tip.style.left = x + "px"; tip.style.top = y + "px";
    return true;
  }
  function hide() {
    clearTimeout(timer); clearTimeout(hideTimer); timer = null;
    if (tip) tip.classList.remove("on");
  }

  document.addEventListener("pointerover", (e) => {
    if (e.pointerType !== "mouse") return;
    const btn = e.target.closest && e.target.closest(".pbtn"); if (!btn) return;
    if (e.relatedTarget && btn.contains(e.relatedTarget)) return;
    hide(); timer = setTimeout(() => show(btn), HOVER_MS);
  }, true);
  document.addEventListener("pointerout", (e) => {
    if (e.pointerType !== "mouse") return;
    const btn = e.target.closest && e.target.closest(".pbtn"); if (!btn) return;
    if (e.relatedTarget && btn.contains(e.relatedTarget)) return;
    hide();
  }, true);

  document.addEventListener("pointerdown", (e) => {
    const btn = e.target.closest && e.target.closest(".pbtn");
    hide(); suppressClick = false;
    if (!btn || e.pointerType === "mouse") return;
    start = { x: e.clientX, y: e.clientY };
    timer = setTimeout(() => { if (show(btn)) suppressClick = true; }, PRESS_MS);
  }, true);
  document.addEventListener("pointermove", (e) => {
    if (!start || e.pointerType === "mouse") return;
    if (Math.abs(e.clientX - start.x) > 10 || Math.abs(e.clientY - start.y) > 10) { start = null; hide(); }
  }, true);
  const release = () => {
    start = null; clearTimeout(timer); timer = null;
    if (suppressClick) hideTimer = setTimeout(hide, SHOW_MS);
  };
  document.addEventListener("pointerup", release, true);
  document.addEventListener("pointercancel", release, true);

  // Nach langem Drücken die Taste NICHT auslösen. Wird vor dem Klick-Handler
  // aus DOMContentLoaded.js registriert (dieses Skript steht davor im HTML).
  document.addEventListener("click", (e) => {
    if (!suppressClick) return;
    suppressClick = false;
    if (e.target.closest && e.target.closest(".pbtn")) { e.preventDefault(); e.stopImmediatePropagation(); }
  }, true);
  // Mausklick blendet den Hilfetext aus.
  document.addEventListener("mousedown", hide, true);

  // Doppelte Tooltips vermeiden (Browser-"title") und fehlende Einträge melden.
  document.addEventListener("DOMContentLoaded", () => {
    const debug = /[?&]helpdebug=1/.test(location.search);
    document.querySelectorAll(".pbtn").forEach((b) => {
      if (helpOf(b)) b.removeAttribute("title");
      else if (debug && !b.classList.contains("lower") && !/^[0-9]$/.test(keyOf(b))) console.log("[paletteHelp] ohne Text:", keyOf(b));
    });
  });
})();
