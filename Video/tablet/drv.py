# Tablet-Treiber: findet Tasten per CDP, tippt per adb (echte Touches).
import json, subprocess, time, urllib.request, websocket
ADB = ["adb", "-s", "HA27SS17"]
_ws = None; _id = 0
def page_id():
    for t in json.load(urllib.request.urlopen("http://localhost:9222/json")):
        if t["type"] == "page" and "doit.cgi" in t["url"]: return t["id"]
def conn(tid=None):
    global _ws
    _ws = websocket.create_connection(f"ws://localhost:9222/devtools/page/{tid or page_id()}", suppress_origin=True)
def cdp(method, **params):
    global _id; _id += 1; _ws.send(json.dumps({"id": _id, "method": method, "params": params}))
    while True:
        r = json.loads(_ws.recv())
        if r.get("id") == _id: return r.get("result", {})
def js(expr):
    r = cdp("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
    return r.get("result", {}).get("value")
def geom():
    # CSS-px -> Bildschirm-px: Viewport liegt unten bündig über der Navigationsleiste
    g = js("({ih:innerHeight, iw:innerWidth, dpr:devicePixelRatio})")
    sz = subprocess.run(ADB + ["shell", "wm", "size"], capture_output=True, text=True).stdout
    H = int(sz.strip().split("x")[-1]); return g, H
def rect(sel):
    return js(f"""(()=>{{const b=document.querySelector({json.dumps(sel, ensure_ascii=False)}); if(!b) return null;
      const r=b.getBoundingClientRect(); return {{x:r.x+r.width/2, y:r.y+r.height/2, top:r.top, bottom:r.bottom}}}})()""")
TOP = 203; DPR = 1.5
def calibrate():
    global TOP, DPR
    g = js("({ih:innerHeight, dpr:devicePixelRatio, sy:screenY, oh:outerHeight})"); DPR = g["dpr"]
    return g
def tap_xy(x, y, hold=0):
    X, Y = round(x * DPR), round(y * DPR + TOP)
    if hold: subprocess.run(ADB + ["shell", "input", "swipe", str(X), str(Y), str(X), str(Y), str(hold)])
    else:    subprocess.run(ADB + ["shell", "input", "tap", str(X), str(Y)])
def ensure_visible(sel):
    ok = js(f"""(()=>{{const b=document.querySelector({json.dumps(sel, ensure_ascii=False)}); if(!b) return null;
      const r=b.getBoundingClientRect(); if(r.top>=0 && r.bottom<=innerHeight) return true;
      b.scrollIntoView({{block:'center', behavior:'smooth'}}); return false}})()""")
    if ok is False: time.sleep(0.8)
HL = 0          # >0: Taste so viele Sekunden vor dem Tippen hervorheben (Video)
def mark(sel, on):
    # eigene Ebene über der Seite (position:fixed) – wird von keinem overflow-Container abgeschnitten
    js(f"""(()=>{{let h=document.getElementById('vidHL'); if(h) h.remove(); if(!{'true' if on else 'false'}) return;
      const b=document.querySelector({json.dumps(sel, ensure_ascii=False)}); if(!b) return; const r=b.getBoundingClientRect();
      h=document.createElement('div'); h.id='vidHL';
      h.style.cssText='position:fixed;pointer-events:none;z-index:99998;border:4px solid #e3007d;border-radius:8px;'+
        'box-shadow:0 0 14px 6px rgba(227,0,125,.55);left:'+(r.left-6)+'px;top:'+(r.top-6)+'px;width:'+(r.width+4)+'px;height:'+(r.height+4)+'px';
      document.body.appendChild(h)}})()""")
def tap(sel, hold=0, pause=0.6):
    ensure_visible(sel)
    r = rect(sel)
    if r is None: raise SystemExit(f"nicht gefunden: {sel}")
    if HL and sel.startswith(".pbtn"):
        mark(sel, True); time.sleep(HL)
        tap_xy(r["x"], r["y"], hold); time.sleep(0.35); mark(sel, False); time.sleep(max(pause - 0.35, 0.1))
    else:
        tap_xy(r["x"], r["y"], hold); time.sleep(pause)
def key(ins, **kw):  return tap(f'.pbtn[data-ins={json.dumps(ins, ensure_ascii=False)}]', **kw)
def cmd(name, **kw): return tap(f'.pbtn[data-cmd="{name}"]', **kw)
def value(): return js("document.getElementById('mf').value")
