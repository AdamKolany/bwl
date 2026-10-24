# Baut stackbwl/editor.html aus einer echten bwl-Fragenseite: nur Antwortfeld + Tastatur, ohne Aufgabe, Lösung und „weiter“.
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
head = s[s.index("<head"):s.index("</head>")]
# Ereignisprotokoll wie in bwl, aber an doit.cgi und als Seite "moodle" gekennzeichnet (Kontext schreibt bridge.js dazu)
head = re.sub(r"(<script[^>]*eventLog\.js[^>]*></script>)",
              r'<script>window.__evlogEndpoint = "/cgi-bin/teste/bwl/doit.cgi?action=log"; window.__evlogAction = "moodle";</script>\1', head)
head = re.sub(r"<script[^>]*jsdelivr[^>]*></script>", "", head)
head = re.sub(r"<script[^>]*mathjax4[^>]*></script>", "", head)

# In der STACK-Sandbox ist der Ursprung "null": MathLives Tastatur-Proxy schickt postMessage(…, "null") an window.top und scheitert.
# bwl nutzt die MathLive-Bildschirmtastatur nicht – Platzhalter vorab setzen, dann legt MathLive keinen Proxy an.
STUB = """<script>if (window !== window.top) { const noop = () => {}; window.mathVirtualKeyboard = { visible: false, isShifted: false,
  boundingRect: new DOMRect(0, 0, 0, 0), layouts: ["default"], connect: noop, disconnect: noop, show: noop, hide: noop, update: noop,
  updateToolbar: noop, executeCommand: () => false, addEventListener: noop, removeEventListener: noop, dispatchEvent: () => true,
  originValidator: "none", targetOrigin: "*", container: null, editToolbar: "none", setKeycap: noop, getKeycap: noop }; }</script>"""
head = head.replace("<head>", "<head>" + STUB, 1)
fs = s[s.index("<fieldset>"):s.index("</fieldset>") + len("</fieldset>")]
fs = re.sub(r"<legend>.*?</legend>", "", fs, flags=re.S)
fs = re.sub(r"<button class=\"btn\" type=\"submit\".*?</button>", "", fs, flags=re.S)       # „weiter“
fs = re.sub(r"data-answer=\"[^\"]*\"", "data-answer=\"\"", fs)                               # keine Lösung im Browser
fs = re.sub(r"(<math-field id=\"mf\"[^>]*>).*?(</math-field>)", r"\1\2", fs, flags=re.S)
scripts = "".join(re.findall(r"<script src=\"/js/(?:abitur/prettyMathJSON|bwl/paletteHelp|bwl/DOMContentLoaded)[^>]*></script>", s))
page = f"""<!DOCTYPE html>
<html lang="de">
{head}
<style> body {{ margin: 0; zoom: 1; }} .box {{ margin: 0 !important; padding: 6px !important; }} fieldset {{ margin: 0; min-width: 0; }}
 #stackStatus {{ font: 12px monospace; color: #888; margin: 2px 4px; min-height: 1.2em; }} </style>
</head>
<body><div class="box"><div id="mathwrap">
{fs}
<div id="stackStatus"></div><div id="js_err" style="color:#a00; white-space:pre-wrap; font-size:14px;"></div>
<script src="/stackbwl/mj2max.js"></script>
<script src="/stackbwl/max2tex.js"></script>
{scripts}
<script src="/stackbwl/bridge.js"></script>
<style> #palette .btnrow {{ flex-wrap: nowrap !important; }} #palette .btnrow.algebraRow {{ padding: 0 !important; }} </style>
<script>
// In der Moodle-Spalte ist der Editor oft schmaler als jedes bwl-Layout (iPad: < 900 px, dann greift weder die
// Tablet-Regel noch paletteFit, das bwl nur am PC ausführt). Hier deshalb immer: Zeilen einzeilig, gemeinsam per
// zoom so skaliert, dass die breiteste in die Palette passt (gleiche Rechnung wie paletteFit in DOMContentLoaded.js).
(function () {{
  function fit() {{
    const pal = document.getElementById("palette"); if (!pal) return;
    const mf = document.getElementById("mf"); const nav = pal.querySelector(".btnrow.navrow");
    const rows = [...pal.querySelectorAll(".btnrow")].filter((r) => r !== nav);
    rows.forEach((r) => (r.style.zoom = ""));
    const extent = (r) => {{ const k = [...r.children].map((c) => c.getBoundingClientRect()).filter((b) => b.width);
      return k.length ? Math.max(...k.map((b) => b.right)) - Math.min(...k.map((b) => b.left)) : 0; }};
    const widest = Math.max(...rows.map(extent)); if (!(widest > 0)) return;
    const z = Math.min(1.4, (pal.clientWidth * 0.97 - 4) / widest);   // etwas Luft für Rahmen/Rundung
    rows.forEach((r) => (r.style.zoom = z.toFixed(4)));
    if (nav && mf) {{ nav.style.zoom = ""; if (nav.scrollWidth > pal.clientWidth) nav.style.zoom = (pal.clientWidth / nav.scrollWidth).toFixed(4); }}
  }}
  addEventListener("load", () => setTimeout(fit, 50)); addEventListener("resize", () => setTimeout(fit, 50));
  setTimeout(fit, 800);
}})();
</script>
<script>document.addEventListener("DOMContentLoaded", function () {{ document.querySelectorAll(".mathbtn").forEach(function (el) {{ const tex = el.dataset.tex; if (tex) katex.render(tex, el, {{ throwOnError: false }}); }}); }});</script>
</div></div></body></html>
"""
open(sys.argv[2], "w", encoding="utf-8").write(page)
print(len(page), "Bytes")
