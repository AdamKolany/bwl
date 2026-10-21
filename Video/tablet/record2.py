# Schulungsvideo v02: eine längere Formel aufbauen, Fehler machen und korrigieren,
# markieren, kopieren, einfügen. Ziel-Formel in einer Sprechblase.
import os, signal, subprocess, sys, time
import drv, bubble, edit_steps as S
from edit_steps import keys, FR, PW, P, SQRT, C3, E

OUT = sys.argv[1] if len(sys.argv) > 1 else "v2take"
DRY = "--dry" in sys.argv
HOST = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "http://mathe-c10-mua.inw.hs-merseburg.de"
BASE = HOST + "/cgi-bin/teste/bwl/doit.cgi"
WANT = r"f(x)=\frac{\sqrt[2]{x^2+1}}{\left(2x-3\right)^3}-\frac{x}{\sqrt[2]{x^2+1}}+\mathbf{e}^{-\frac{x}{2}}"

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
    time.sleep(hold)
def end_sub():
    global cur
    rest = cur[0] + need(cur[1]) - (time.time() - T0)
    if rest > 0: time.sleep(rest)
    subs.append((cur[0], time.time() - T0, cur[1])); cur = None
def chk(tag): print(f"   {tag}: {drv.value()}", flush=True)
def goto(url, wait=4):
    drv.js(f"location.href='{url}'"); time.sleep(wait); drv.conn()

drv.conn()
goto(f"{BASE}?action=menu&kapitel=TSTA&thema=abltn", wait=3)
drv.tap("button[value=start]", pause=4); drv.conn()
drv.js("window.scrollTo(0,0)"); time.sleep(1)
print(bubble.task()); drv.HL = 0.8

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
try:
    say("Formeln bearbeiten: korrigieren, markieren, kopieren und einfügen", 2)
    say("Die Aufgabe: diese Formel soll ins Antwortfeld.", 3)
    say("Die Taste, die als Nächstes gedrückt wird, ist jeweils farbig umrandet.", 2)
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
    drv.js("window.scrollTo({top:document.querySelector('p.q').getBoundingClientRect().top+scrollY-8,behavior:'smooth'})"); time.sleep(1.2)
    say("Vergleichen Sie mit der Aufgabe: im ersten Nenner steht + 3 statt − 3!", 3)
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
