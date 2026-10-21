# Einzelschritte für das Editier-Video; im Probelauf wird nach jedem Schritt der Wert gezeigt.
import json, time, drv
FR = "\\frac{#0}{{#?}}"; PW = "#0^{#?}"; P = "\\left(#0\\right)"; SQRT = "\\sqrt[2]{#0}"; C3 = "#0^3"; E = "\\mathbf{e}"
PAUSE = 0.9
def op(o, pause=None):
    pause = PAUSE if pause is None else pause
    if o.startswith("!"): drv.cmd(o[1:], pause=pause)
    elif len(o) == 1 and o.isalpha(): drv.tap(f'.pbtn[data-base="{o.lower()}"]', pause=pause)
    else: drv.key(o, pause=pause)
def keys(*ops):
    for o in ops: op(o)
def tap_in_formula(char, which="lowest-left"):
    """Tippt im Antwortfeld rechts auf das Zeichen char (z. B. '+') – setzt den Cursor dahinter."""
    r = drv.js("""(()=>{const mf=document.getElementById('mf'); const out=[];
      const walk=n=>{ if(n.nodeType===3){ if(n.textContent.trim()===%s){const s=n.parentElement.getBoundingClientRect(); if(s.width) out.push([s.right,s.top+s.height/2,s.width]);} }
                     else n.childNodes.forEach(walk); };
      walk(mf.shadowRoot); return out})()""" % json.dumps(char))
    print("   kandidaten", r)
    ymax = max(c[1] for c in r)
    low = [c for c in r if c[1] > ymax - 8]
    c = min(low, key=lambda c: c[0])
    drv.tap_xy(c[0] - c[2] * 0.2, c[1]); time.sleep(1)
