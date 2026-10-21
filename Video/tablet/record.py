# Schulungsvideo: Bildschirmtastatur. Steuert das Tablet, nimmt per scrcpy auf
# und schreibt Untertitel (SRT) mit Zeitstempeln.
import os, signal, subprocess, sys, time
import drv

OUT = sys.argv[1] if len(sys.argv) > 1 else "take"
DRY = "--dry" in sys.argv
BASE = "http://mathe-c10-mua.inw.hs-merseburg.de/cgi-bin/teste/bwl/doit.cgi"
P = "\\left(#0\\right)"; FR = "\\frac{#0}{{#?}}"; SQ = "#0^2"; PW = "#0^{#?}"; NF = "#0^{{#?}/{#?}}"
E = "\\mathbf{e}"; SIN = "\\sin\\left(#0\\right)"; LN = "\\ln\\left(#0\\right)"
KEY_PAUSE = 0.9

T0 = None; subs = []; cur = None
def say(text, hold=2.5):
    """Untertitel ab jetzt; bleibt bis zum nächsten say()."""
    global cur
    t = time.time() - T0
    if cur: subs.append((cur[0], t, cur[1]))
    cur = (t, text); print(f"[{t:6.1f}] {text}", flush=True)
    time.sleep(hold)
def end_sub():
    global cur
    if cur: subs.append((cur[0], time.time() - T0, cur[1])); cur = None

def op(o, pause=KEY_PAUSE):
    if o.startswith("!"): drv.cmd(o[1:], pause=pause)
    elif len(o) == 1 and o.isalpha(): drv.tap(f'.pbtn[data-base="{o.lower()}"]', pause=pause)
    else: drv.key(o, pause=pause)
def keys(*ops):
    for o in ops: op(o)
def goto(url, wait=4):
    drv.js(f"location.href='{url}'"); time.sleep(wait); drv.conn()
def screen_tap(x, y, pause=1.5):
    subprocess.run(drv.ADB + ["shell", "input", "tap", str(x), str(y)]); time.sleep(pause)
def scroll_top():
    drv.js("window.scrollTo({top:0,behavior:'smooth'})"); time.sleep(1)
def focus_answer():
    drv.tap("#mf", pause=1.2)
def submit():
    drv.tap("button.btn[value=save]", pause=4); drv.conn()
def via_menu(thema, label):
    goto(f"{BASE}?action=menu&kapitel=TSTA&thema={thema}", wait=3)
    say(f"Nächstes Thema: {label}", 2.5)
    drv.tap("button[value=start]", pause=4); drv.conn()
    scroll_top(); time.sleep(1.5)
results = []
def check(name):
    v = drv.js("document.getElementById('mf').value"); results.append((name, v)); print("   ->", v)

# ---------------------------------------------------------------- Aufnahme
drv.conn()
goto(f"{BASE}?action=menu", wait=3)
rec = None
if not DRY:
    rec = subprocess.Popen(["scrcpy", "-s", "HA27SS17", "--no-window", "--no-audio",
                            "--max-fps=30", f"--record={OUT}.mp4"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # erst loslegen, wenn scrcpy wirklich Bilder schreibt
    for _ in range(100):
        if os.path.exists(f"{OUT}.mp4") and os.path.getsize(f"{OUT}.mp4") > 1000: break
        time.sleep(0.2)
    time.sleep(2)
T0 = time.time()
try:
    # --- Einstieg: Menü -------------------------------------------------
    say("Formeleingabe mit der Bildschirmtastatur – eine kurze Einführung", 3.5)
    say("Wählen Sie zuerst das Kapitel …", 1.5)
    drv.tap("select[name=kapitel]", pause=1.5); screen_tap(610, 522, 4); drv.conn()
    say("… dann das Thema, z. B. „Ableitungen“", 1.5)
    drv.tap("select[name=thema]", pause=1.5); screen_tap(560, 177, 3.5); drv.conn()
    say("Mit „Start“ geht es los.", 1.5)
    drv.tap("button[value=start]", pause=4); drv.conn(); scroll_top()

    # --- 1. Ableitungen: e, Markieren, Potenz, heraus, sin -----------------
    say("Oben steht die Aufgabe, unten tragen Sie Ihre Antwort ein.", 3.5)
    say("Tippen Sie in das Antwortfeld – darunter erscheint die Tastatur.", 1.5)
    focus_answer(); time.sleep(1.5)
    say("Tipp: Taste etwas länger gedrückt halten – dann erscheint ein Hilfetext.", 1)
    drv.cmd("exitCtx", hold=900, pause=3.5)
    say("Ergebnis: f′(x) = −4 · e^{4x} · sin(e^{4x})", 2.5)
    say("Zuerst −4 und der Malpunkt …", 0.5); keys("-", "4", "·")
    say("Die Eulersche Zahl e hat eine eigene Taste.", 0.5); keys(E)
    say("Potenz: erst die Basis markieren – mit dem schwarzen Dreieck ◀ …", 0.5); keys("!selL")
    time.sleep(1)
    say("… dann die Potenz-Taste. Der Cursor steht jetzt im Exponenten.", 0.5); keys(PW)
    keys("4", "x")
    say("Mit der Taste „heraus“ verlassen Sie den Exponenten.", 0.5); keys("!exitCtx")
    keys("·")
    say("Funktionen wie sin bringen ihre Klammer gleich mit.", 0.5); keys(SIN)
    say("Im Argument noch einmal: e, markieren ◀, Potenz, 4x.", 0.5)
    keys(E, "!selL", PW, "4", "x")
    check("abltn")
    say("Fertig – mit „weiter“ wird die Antwort abgeschickt.", 1.5)
    submit(); time.sleep(2.5)

    # --- 2. Ausklammern: Klammer, ganze Klammer markieren, Quadrat ---------
    via_menu("auskl", "Ausklammern")
    say("Ergebnis: (x − 2y)²", 2)
    focus_answer()
    say("Die Klammer-Taste setzt beide Klammern auf einmal.", 0.5); keys(P)
    keys("x", "-", "2", "y")
    say("„heraus“ – der Cursor steht hinter der Klammer.", 0.5); keys("!exitCtx")
    say("◀ markiert die ganze Klammer …", 0.5); keys("!selL"); time.sleep(0.8)
    say("… und die Quadrat-Taste setzt das Quadrat darauf.", 0.5); keys(SQ)
    check("auskl")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 3. Ausmultiplizieren: Korrigieren, Rückgängig/Wiederholen ---------
    via_menu("ausml", "Ausmultiplizieren")
    say("Ergebnis: x² − xy − 12y²", 2)
    focus_answer()
    say("x, markieren ◀, Quadrat-Taste.", 0.5); keys("x", "!selL", SQ)
    keys("-", "x", "y", "-", "1", "3")
    say("Vertippt? Die Löschtaste ⌫ entfernt das Zeichen links vom Cursor.", 0.5); keys("!bs")
    keys("2", "y", "!selL", SQ)
    say("Rückgängig ↶ und Wiederholen ↷ funktionieren wie gewohnt.", 0.5)
    keys("!undo"); time.sleep(0.6); keys("!redo")
    check("ausml")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 4. Bruchterme: Bruch-Taste, Zähler -> Nenner ----------------------
    via_menu("brtrm", "Bruchterme")
    say("Ergebnis: (x² + x + 2) / (x² − 4)", 2)
    focus_answer()
    say("Die Bruch-Taste legt Zähler und Nenner an. Der Cursor steht im Zähler.", 0.5); keys(FR)
    keys("x", "!selL", SQ, "+", "x", "+", "2")
    say("Pfeil → springt vom Zähler in den Nenner.", 0.5); keys("!move_R")
    keys("x", "!selL", SQ, "-", "4")
    check("brtrm")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 5. Doppelbrüche: erst schreiben, dann markieren, dann Bruch -------
    via_menu("dopbr", "Doppelbrüche")
    say("Ergebnis: (x − 10)(4x + 10) / (x − 20)", 2)
    focus_answer()
    say("Diesmal schreiben wir den Zähler zuerst …", 0.5)
    keys(P, "x", "-", "1", "0", "!exitCtx", "·", P, "4", "x", "+", "1", "0", "!exitCtx")
    say("… markieren ihn mit dreimal ◀ …", 0.5); keys("!selL", "!selL", "!selL"); time.sleep(0.8)
    say("… und die Bruch-Taste macht ihn zum Zähler.", 0.5); keys(FR)
    keys("x", "-", "2", "0")
    check("dopbr")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 6. Polynomdivision: Cursor bewegen, einfügen ----------------------
    via_menu("pldiv", "Polynomdivision")
    say("Ergebnis: x² + 6x + 11", 2)
    focus_answer()
    keys("x", "!selL", SQ, "+", "1", "1")
    say("„+ 6x“ vergessen? Mit ← den Cursor zurücksetzen …", 0.5); keys("!move_L", "!move_L", "!move_L")
    say("… und einfach einfügen.", 0.5); keys("+", "6", "x")
    check("pldiv")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 7. Stammfunktionen: ln -----------------------------------------
    via_menu("stamf", "Stammfunktionen")
    say("Ergebnis: ln(x² + 7) + 1 − ln 7", 2)
    focus_answer()
    say("Auch ln setzt die Klammer automatisch.", 0.5); keys(LN)
    keys("x", "!selL", SQ, "+", "7")
    say("„heraus“ aus der Klammer, dann weiter.", 0.5); keys("!exitCtx")
    keys("+", "1", "-", LN, "7")
    check("stamf")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 8. Unbestimmte Integrale: Bruch-Exponent, Großbuchstabe -----------
    via_menu("unint", "Unbestimmte Integrale")
    say("Ergebnis: ⅓ (x² + 1)^{3/2} + C", 2)
    focus_answer()
    keys(FR, "1", "!move_R", "3", "!exitCtx")
    keys(P, "x", "!selL", SQ, "+", "1", "!exitCtx")
    say("Klammer markieren ◀ – dann die Taste „Potenz mit Bruch im Exponenten“.", 0.5)
    keys("!selL", NF, "3", "!move_R", "2", "!exitCtx")
    keys("+")
    say("Großbuchstaben: ⇧ einmal antippen – der nächste Buchstabe wird groß.", 0.5)
    keys("!capsCycle", "C")
    check("unint")
    say("Abschicken mit „weiter“.", 1); submit(); time.sleep(2.5)

    # --- 9. Weitere Tasten ----------------------------------------------
    via_menu("abltn", "Weitere Tasten (zum Ausprobieren)")
    focus_answer()
    say("Wurzeln: Quadratwurzel …", 0.5)
    keys("\\sqrt[2]{#0}", "x", "!selL", SQ, "+", "3", "!exitCtx")
    say("Kopieren: Wurzel markieren ◀, dann →📋 …", 0.5); keys("!selL"); time.sleep(0.6); keys("!copy")
    say("… und mit 📋→ an der Cursorstelle einfügen.", 0.5); keys("!move_R", "+", "!paste")
    time.sleep(1)
    say("Dritte und n-te Wurzel haben eigene Tasten.", 0.5)
    keys("+", "\\sqrt[3]{#0}", "8", "!exitCtx", "+", "\\sqrt[#?]{#0}")
    time.sleep(1)
    say("★ markiert alles, ⊠ löscht die Auswahl.", 0.5); keys("!selectAll"); time.sleep(0.8); keys("!clear")
    say("Integral mit Grenzen: ∫, markieren ◀, Index-Taste für die untere Grenze …", 0.5)
    keys("\\int", "!selL", "#0_{#?}", "0", "!exitCtx")
    say("… markieren ◀, Potenz-Taste für die obere Grenze.", 0.5)
    keys("!selL", PW, "1", "!exitCtx", "x", "!selL", SQ, "\\,\\text{d}", "x")
    time.sleep(1)
    say("Summe – genauso: ∑, Index, Potenz.", 0.5)
    keys("+", "\\sum", "!selL", "#0_{#?}", "k", "=", "1", "!exitCtx", "!selL", PW, "n", "!exitCtx", "k")
    check("extra")
    time.sleep(1.5)
    say("Viel Erfolg beim Üben!", 3.5)
    end_sub()
finally:
    if rec:
        rec.send_signal(signal.SIGINT); rec.wait(timeout=20)

def ts(t):
    t = max(t, 0); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
with open(f"{OUT}.srt", "w", encoding="utf-8") as f:
    for i, (a, b, txt) in enumerate(subs, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
print("RESULTS"); [print(" ", n, v) for n, v in results]
