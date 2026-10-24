# Schulungsvideo v03_06: Zielformel steht schon da, wenn der Überblick angesagt wird; ⇧ mit allen
# drei Zuständen im Zähler des 2. Bruchs; ← → laufen bis in die Wurzel, „heraus“ dreimal
# (Exponent, Wurzel, Bruch); e^{−x/2} mit der Taste □^{□/□}; „Los geht’s“ entfällt.
# Schulungsvideo v03_04: wie v03, aber der Überblick über die Sondertasten wird an der fertigen
# Zielformel vorgeführt (echte Hilfetexte, ⌫ ⌦ ↶ ↷ ⊠ 📋 im Einsatz); Aufnahme auf main (ohne :8080).
# Schulungsvideo v03: wie v02, aber die ganze Tastatur bleibt sichtbar und es gibt
# vorab einen Überblick über die Sondertasten (langes Drücken zeigt den Hilfetext).
# Schreibt <OUT>.mp4 (scrcpy), <OUT>.srt und <OUT>.layout.json (Lage von Formel und
# Sondertasten im Video-Bild, für die Nachbearbeitung).
import json, os, signal, subprocess, sys, time
import drv, bubble, edit_steps as S
from edit_steps import keys, FR, PW, P, SQRT, C3, E

OUT = sys.argv[1] if len(sys.argv) > 1 else "v3take"
DRY = "--dry" in sys.argv
HOST = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "http://mathe-c10-mua.inw.hs-merseburg.de"
BASE = HOST + "/cgi-bin/teste/bwl/doit.cgi"
WANT = r"f(x)=\frac{\sqrt[2]{x^2+1}}{\left(2x-3\right)^3}-\frac{x}{\sqrt[2]{x^2+1}}+\mathbf{e}^{-x/2}"
CROP_Y = 58          # Statusleiste, wird im Schnitt abgeschnitten
HOLD = 1500          # ms langes Drücken -> Hilfetext

T0 = None; subs = []; cur = None
def need(text): return max(4.0, 1.8 + len(text) / 11)     # Lesezeit
def say(text, hold=1.5):
    """Neuer Untertitel – aber erst, wenn der vorige lange genug zu lesen war."""
    global cur
    if cur:
        rest = cur[0] + need(cur[1]) - (time.time() - T0)
        if rest > 0: time.sleep(rest)
        subs.append((cur[0], time.time() - T0, cur[1]))
    cur = (time.time() - T0, text); print(f"[{cur[0]:6.1f}] {text}", flush=True)
    kb_fit()
    time.sleep(hold)
def end_sub():
    global cur
    rest = cur[0] + need(cur[1]) - (time.time() - T0)
    if rest > 0: time.sleep(rest)
    subs.append((cur[0], time.time() - T0, cur[1])); cur = None
def chk(tag): print(f"   {tag}: {drv.value()}", flush=True)
def goto(url, wait=4):
    drv.js(f"location.href='{url}'"); time.sleep(wait); drv.conn()

def kb_fit(smooth=True):
    """Seite so scrollen, dass die unterste Tastenzeile gerade noch ganz sichtbar ist."""
    d = drv.js("(()=>{const r=[...document.querySelectorAll('.btnrow')].pop().getBoundingClientRect(); return Math.round(r.bottom-innerHeight+4)})()")
    if d and abs(d) > 3:
        drv.js(f"window.scrollBy({{top:{d},behavior:'{'smooth' if smooth else 'auto'}'}})"); time.sleep(0.9 if smooth else 0.2)

def frame_box(sel):
    """Rechteck eines Elements in Video-Koordinaten (1920x1200 nach dem Zuschnitt)."""
    r = drv.js(f"""(()=>{{const e=document.querySelector({json.dumps(sel, ensure_ascii=False)}); if(!e) return null;
      const b=e.getBoundingClientRect(); return [b.left,b.top,b.right,b.bottom]}})()""")
    if not r: return None
    return [round(r[0] * drv.DPR), round(r[1] * drv.DPR + drv.TOP - CROP_Y), round(r[2] * drv.DPR), round(r[3] * drv.DPR + drv.TOP - CROP_Y)]

PREFIX = "f(x)="
NF = "#0^{{#?}/{#?}}"     # Potenz mit Schrägstrich-Bruch im Exponenten
def val(): return drv.js("document.getElementById('mf').value")
def setval(v, pos=None):
    drv.js("(()=>{const m=document.getElementById('mf'); m.value=%s; m.focus(); m.position=%s})()" % (json.dumps(v), "m.lastOffset" if pos is None else pos))
POS_X2 = 30          # in WANT: hinter dem x im Zähler des zweiten Bruchs
def hold_key(sel): drv.tap(sel, hold=HOLD, pause=0.9)
SPECIAL = ["capsCycle", "exitCtx", "bs", "del", "clear", "selL", "selR", "selectAll", "move_L", "move_R", "copy", "paste", "undo", "redo"]
def explain(text, *cmds, hold=0.3):
    say(text, hold)
    for c in cmds: drv.cmd(c, hold=HOLD, pause=0.9)

import urllib.request    # auf dem Tablet sind mehrere doit.cgi-Tabs offen: den :8080-Tab nehmen
TID = "36"   # dritter Tab; IDs: curl localhost:9222/json
urllib.request.urlopen(f"http://localhost:9222/json/activate/{TID}"); drv.page_id = lambda: TID
drv.conn(); drv.calibrate()
goto(f"{BASE}?action=menu&kapitel=TSTA&thema=abltn", wait=3)
drv.tap("button[value=start]", pause=4); drv.conn()
drv.js("window.scrollTo(0,0)"); time.sleep(1)
print(bubble.task()); time.sleep(1); drv.HL = 0.8
layout = {"formula": frame_box("p.q math-field")}

rec = None
if not DRY:
    rec = subprocess.Popen(["scrcpy", "-s", "HA27SS17", "--no-window", "--no-audio",
                            "--max-fps=30", f"--record={OUT}.mp4"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if os.path.exists(f"{OUT}.mp4") and os.path.getsize(f"{OUT}.mp4") > 1000: break
        time.sleep(0.2)
    time.sleep(2)
# Sync-Marke: kurz schwarzer Bildschirm; T0 = Moment, in dem er verschwindet
drv.js("(()=>{const d=document.createElement('div');d.id='syncMark';d.style.cssText='position:fixed;inset:0;background:#000;z-index:99999';document.body.appendChild(d)})()")
time.sleep(1.0)
drv.js("document.getElementById('syncMark').remove()"); T0 = time.time()
_kb_fit = kb_fit; kb_fit = lambda smooth=True: None      # am Anfang noch nicht scrollen
try:
    say("Formeln bearbeiten: korrigieren, markieren, kopieren und einfügen", 2)
    say("Die Aufgabe: diese Formel soll ins Antwortfeld.", 3)
    kb_fit = _kb_fit; layout["scrolled_at"] = time.time() - T0; kb_fit()
    layout["keys"] = {c: frame_box(f'.pbtn[data-cmd="{c}"]') for c in SPECIAL}
    say("Die Taste, die als Nächstes gedrückt wird, ist jeweils farbig umrandet.", 2)

    # --- Überblick über die Sondertasten, vorgeführt an der fertigen Formel (v03_04) ---
    setval(WANT, POS_X2); time.sleep(0.3)   # Formel steht schon da, bevor der Satz beginnt; Cursor im Zähler des 2. Bruchs
    say("Zuerst ein kurzer Überblick über die Sondertasten – gleich an der fertigen Formel.", 3.0)
    say("Tipp: Halten Sie eine Taste etwas länger gedrückt – dann erscheint eine kurze Erklärung. Die Taste wird dabei nicht ausgelöst.", 1.5)
    hold_key('.pbtn[data-cmd="exitCtx"]'); hold_key(f'.pbtn[data-ins={json.dumps(FR)}]')
    hold_key('.pbtn[data-ins="\\\\sqrt[#?]{#0}"]'); hold_key('.pbtn[data-ins="\\\\lim\\\\limits_{n\\\\to\\\\infty}"]'); chk("nach Tipp")
    say("⇧ einmal tippen: nur der nächste Buchstabe wird groß.", 0.5)
    keys("!capsCycle", "a", "b"); chk("caps shift")                 # → „Ab“
    say("⇧ zweimal tippen: alle Buchstaben groß – bis Sie ⇧ ein drittes Mal tippen.", 0.5)
    keys("!capsCycle", "!capsCycle", "c", "d", "!capsCycle", "e"); chk("caps lock")   # → „AbCDe“
    say("⌫ löscht die Buchstaben wieder.", 0.5)       # (az ↔ AZ ist auf der Tastatur ausgeblendet)
    keys("!bs", "!bs", "!bs", "!bs", "!bs"); chk("caps weg")
    say("Die Tasten ← → bewegen den Cursor Schritt für Schritt – vom Zähler in den Nenner, in die Wurzel und in den Exponenten.", 0.5)
    drv.HL = 0.45
    for _ in range(8): S.op("!move_R", pause=0.55)        # Nenner, Wurzelindex, Wurzel, x, Exponent, hinter x²
    drv.HL = 0.8; time.sleep(0.4); keys("!move_L"); chk("im Exponenten")     # Cursor hinter der 2 in x² der zweiten Wurzel
    say("Die Taste ⌫ löscht links vom Cursor – hier die 2 –, und ↶ macht das rückgängig.", 0.5)
    keys("!bs"); time.sleep(0.8); keys("!undo"); chk("bs/undo")
    say("Die Taste ⌦ löscht rechts vom Cursor – auch das macht ↶ wieder rückgängig.", 0.5)
    keys("!move_L", "!del"); time.sleep(0.8); keys("!undo"); chk("del/undo")
    say("Die Taste „heraus“ springt jeweils eine Ebene hinaus: aus dem Exponenten, aus der Wurzel, aus dem Bruch.", 0.3)
    keys("!exitCtx"); time.sleep(1.0); keys("!exitCtx"); time.sleep(1.0); keys("!exitCtx"); chk("heraus x3")
    say("Die schwarzen Dreiecke ◀ ▶ erweitern die Auswahl.", 0.5)
    keys("!selL", "!selL", "!selL"); time.sleep(0.4); keys("!selR")
    say("Die Taste ⊠ löscht die ganze Auswahl, ↶ holt sie zurück, ↷ löscht sie wieder – und noch einmal ↶.", 0.5)
    keys("!clear"); time.sleep(0.8); keys("!undo"); time.sleep(0.6); keys("!redo"); time.sleep(0.6); keys("!undo"); chk("clear/undo/redo")
    say("Die Taste →📋 kopiert die Auswahl, 📋→ fügt sie ein – hier direkt dahinter.", 0.5)
    keys("!copy", "!move_R", "!paste"); time.sleep(1.2); chk("paste")
    keys("!undo"); chk("undo paste")
    say("Die Taste ★ wählt alles aus.", 0.5)
    keys("!selectAll"); time.sleep(1.2); keys("!move_R")
    layout["legend_at"] = time.time() - T0
    say("Diese Übersicht bleibt unten eingeblendet.", 1.5)
    setval(PREFIX); time.sleep(0.3)
    say("Und jetzt geben wir die Formel selbst ein.", 2.0)
    layout["main_at"] = time.time() - T0

    # --- Formel eingeben (wie v02) ---------------------------------------
    drv.tap("#mf", pause=1.2)
    say("Wir beginnen mit dem Bruch: Bruch-Taste – der Cursor steht im Zähler.", 0.5)
    keys(FR)
    say("Im Zähler eine Quadratwurzel.", 0.5); keys(SQRT)
    say("x eingeben, mit ◀ markieren, Potenz-Taste, dann 2 …", 0.5)
    keys("x", "!selL", PW, "2")
    say("… und weiter mit + 1.", 0.5); keys("+", "1"); chk("Fehler 1")
    say("Hoppla: „+ 1“ ist mit in den Exponenten gerutscht!", 2.5)
    say("Korrigieren: zweimal ⌫ löscht „1“ und „+“ wieder …", 0.5); keys("!bs", "!bs")
    say("… „heraus“ verlässt den Exponenten – jetzt erst + 1.", 0.5); keys("!exitCtx", "+", "1")
    say("Noch einmal „heraus“ – der Cursor steht hinter der Wurzel.", 0.5); keys("!exitCtx")
    say("Die Wurzel brauchen wir später noch einmal: mit ◀ markieren …", 0.5); keys("!selL")
    say("… und mit →📋 in die Zwischenablage kopieren.", 0.5); keys("!copy")
    say("→ hebt die Markierung auf, ein zweites → springt in den Nenner.", 0.5); keys("!move_R", "!move_R")
    say("Nenner: 2x + 3", 0.5); keys("2", "x", "+", "3")
    say("Für die Klammer: alles mit viermal ◀ markieren …", 0.5); keys("!selL", "!selL", "!selL", "!selL")
    say("… Klammer-Taste – der markierte Teil steht jetzt in Klammern.", 0.5); keys(P)
    say("→, dann ◀ markiert die ganze Klammer – und hoch 3.", 0.5); keys("!move_R", "!selL", C3)
    say("„heraus“ verlässt den Nenner. Weiter mit Minus und einem neuen Bruch.", 0.5)
    keys("!exitCtx", "-", FR, "x")
    say("→ in den Nenner, und 📋→ fügt die kopierte Wurzel ein.", 0.5); keys("!move_R", "!paste")
    say("„heraus“, dann + e: e, mit ◀ markieren, und die Potenz-Taste mit Schrägstrich-Bruch.", 0.5)
    keys("!exitCtx", "+", E, "!selL", NF)
    say("Im Exponenten: − x, → in den Nenner, dann 2.", 0.5); keys("-", "x", "!move_R", "2")
    say("„heraus“ – fertig?", 0.5); keys("!exitCtx"); chk("Fehler 2")
    layout["compare_at"] = time.time() - T0
    say("Vergleichen Sie mit der Aufgabe oben: im ersten Nenner steht + 3 statt − 3!", 3)
    say("Kein Problem: einfach mit Finger oder Stift direkt hinter das + tippen.", 0.5)
    S.tap_in_formula("+")
    say("Der Cursor steht jetzt dort. ⌫ löscht das +, dann − eingeben.", 0.5); keys("!bs", "-")
    say("Jetzt stimmt die Formel mit der Aufgabe überein.", 2); chk("Ende")
    say("Zum Schluss: Rückgängig und Wiederholen.", 1)
    say("★ markiert alles, ⊠ löscht die Auswahl – die ganze Formel ist weg!", 0.5)
    keys("!selectAll"); keys("!clear"); chk("leer")
    say("Kein Problem: ↶ (Rückgängig) holt sie zurück.", 0.5); keys("!undo"); chk("zurück")
    say("↷ (Wiederholen) macht das Rückgängig-Machen wieder rückgängig – die Formel ist wieder weg …", 0.5); keys("!redo")
    say("… und noch einmal ↶ – alles wieder da.", 0.5); keys("!undo"); chk("wieder da")
    say("Mit „weiter“ würden Sie die Antwort abschicken. Viel Erfolg!", 2)
    end_sub()
finally:
    if rec:
        rec.send_signal(signal.SIGINT); rec.wait(timeout=20)

ok = drv.value() == WANT
print("ERGEBNIS", "OK" if ok else "FALSCH", drv.value())
def ts(t):
    t = max(t, 0); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
with open(f"{OUT}.srt", "w", encoding="utf-8") as f:
    for i, (a, b, txt) in enumerate(subs, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
layout["ok"] = ok
json.dump(layout, open(f"{OUT}.layout.json", "w"), indent=1)
