# Schulungsvideo v03: wie v02, aber die ganze Tastatur bleibt sichtbar und es gibt
# vorab einen Überblick über die Sondertasten (langes Drücken zeigt den Hilfetext).
# Schreibt <OUT>.mp4 (scrcpy), <OUT>.srt und <OUT>.layout.json (Lage von Formel und
# Sondertasten im Video-Bild, für die Nachbearbeitung).
import json, os, signal, subprocess, sys, time
import drv, bubble, edit_steps as S
from edit_steps import keys, FR, PW, P, SQRT, C3, E

OUT = sys.argv[1] if len(sys.argv) > 1 else "v3take"
DRY = "--dry" in sys.argv
HOST = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "http://mathe-c10-mua.inw.hs-merseburg.de:8080"
BASE = HOST + "/cgi-bin/teste/bwl/doit.cgi"
WANT = r"f(x)=\frac{\sqrt[2]{x^2+1}}{\left(2x-3\right)^3}-\frac{x}{\sqrt[2]{x^2+1}}+\mathbf{e}^{-\frac{x}{2}}"
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

SPECIAL = ["capsCycle", "exitCtx", "bs", "del", "clear", "selL", "selR", "selectAll", "move_L", "move_R", "copy", "paste", "undo", "redo"]
def explain(text, *cmds, hold=0.3):
    say(text, hold)
    for c in cmds: drv.cmd(c, hold=HOLD, pause=0.9)

import urllib.request    # auf dem Tablet sind mehrere doit.cgi-Tabs offen: den :8080-Tab nehmen
TID = [t["id"] for t in json.load(urllib.request.urlopen("http://localhost:9222/json")) if t["type"] == "page" and ":8080" in t["url"]][0]
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

    # --- Überblick über die Sondertasten ---------------------------------
    say("Zuerst ein kurzer Überblick über die Sondertasten.", 1.5)
    explain("Tipp: Halten Sie eine Taste etwas länger gedrückt – dann erscheint eine kurze Erklärung. Die Taste wird dabei nicht ausgelöst.", "exitCtx", hold=1.5)
    explain("⇧ Großbuchstaben: einmal tippen – nur der nächste Buchstabe, zweimal – dauerhaft, dreimal – wieder aus.", "capsCycle")
    explain("„heraus“ springt eine Ebene hinaus – aus Exponent, Bruch, Wurzel oder Klammer.", "exitCtx")
    explain("⌫ löscht links vom Cursor, ⌦ rechts davon, ⊠ löscht die Auswahl.", "bs", "del", "clear")
    explain("Die schwarzen Dreiecke ◀ ▶ erweitern die Auswahl, ★ wählt alles aus.", "selL", "selR", "selectAll")
    explain("← → bewegen den Cursor.", "move_L", "move_R")
    explain("→📋 kopiert die Auswahl, 📋→ fügt sie ein.", "copy", "paste")
    explain("↶ macht rückgängig, ↷ wiederholt.", "undo", "redo")
    layout["legend_at"] = time.time() - T0
    say("Diese Übersicht bleibt unten eingeblendet. Los geht’s!", 1.5); chk("nach Überblick")

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
    say("„heraus“, dann + e: e, mit ◀ markieren, Potenz-Taste.", 0.5)
    keys("!exitCtx", "+", E, "!selL", PW)
    say("Im Exponenten: Minus und der Bruch x/2.", 0.5); keys("-", FR, "x", "!move_R", "2")
    say("Zweimal „heraus“ – fertig?", 0.5); keys("!exitCtx", "!exitCtx"); chk("Fehler 2")
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
