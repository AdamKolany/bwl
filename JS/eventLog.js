// Ereignisprotokoll (Diagnose): zeichnet auf, was der Nutzer auf der Seite
// tut — Tasten, Palette-Knöpfe, Tippen/Ziehen (Finger/Stift/Maus, Dauer,
// Weg, Druck), Auswahl im Formelfeld, Kontextmenüs, Schütteln des Geräts
// (mit Stärke), JS-Fehler — und schickt es gebündelt an doit.cgi?action=log
// (Tabelle event_log, DDL in Modules/schema.sql). Nur zur Fehlersuche, falls
// "etwas nicht funktioniert hat". Ohne Tabelle schluckt der Server es still.
(function () {
  "use strict";
  if (window.__evlog) return;

  const ENDPOINT = (location.pathname || "doit.cgi") + "?action=log";
  const FLUSH_MS = 5000, MAX_BUF = 400;
  const t0 = Date.now();
  const pageId = t0.toString(36) + Math.random().toString(36).slice(2, 7);
  const qs = new URLSearchParams(location.search);
  const page = { action: qs.get("action") || "menu", nr: qs.get("nr") || null };
  let seq = 0, buf = [];

  function log(type, data) {
    if (buf.length >= MAX_BUF) buf.shift();
    buf.push({ s: seq++, t: Date.now(), y: type, d: data || null });
  }

  function flush(useBeacon) {
    if (!buf.length) return;
    const nr = (document.querySelector('input[name="nr"]') || {}).value || page.nr;
    const body = JSON.stringify({ p: pageId, a: page.action, nr: nr, ev: buf });
    buf = [];
    try {
      const blob = new Blob([body], { type: "text/plain" });
      if (useBeacon && navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, blob)) return;
      fetch(ENDPOINT, { method: "POST", body: blob, keepalive: true, credentials: "same-origin" }).catch(() => {});
    } catch (_) {}
  }
  setInterval(() => flush(false), FLUSH_MS);
  addEventListener("pagehide", () => { log("pagehide"); flush(true); });
  document.addEventListener("visibilitychange", () => {
    log("visibility", { state: document.visibilityState });
    if (document.visibilityState === "hidden") flush(true);
  });

  // Kurzbeschreibung eines Elements (für "worauf wurde getippt")
  function desc(el) {
    if (!el || !el.tagName) return null;
    const b = el.closest && el.closest("button,[data-cmd],[data-ins],math-field,input,a,label");
    const e = b || el;
    let s = e.tagName.toLowerCase();
    if (e.id) s += "#" + e.id;
    const cmd = e.getAttribute && (e.getAttribute("data-cmd") || e.getAttribute("data-ins"));
    if (cmd) s += "[" + cmd + "]";
    else if (e.name) s += "[name=" + e.name + "]";
    const txt = (e.textContent || "").trim();
    if (!cmd && txt && txt.length <= 12) s += '"' + txt + '"';
    return s;
  }
  const r1 = (x) => Math.round(x * 10) / 10;

  // --- Seite ------------------------------------------------------------
  log("load", {
    ua: navigator.userAgent, vw: innerWidth, vh: innerHeight,
    sw: screen.width, sh: screen.height, dpr: devicePixelRatio,
    orient: (screen.orientation && screen.orientation.type) || null,
    touch: navigator.maxTouchPoints || 0, q: location.search,
  });
  addEventListener("resize", () => log("resize", { vw: innerWidth, vh: innerHeight }));
  addEventListener("orientationchange", () =>
    log("orientation", { o: (screen.orientation && screen.orientation.type) || window.orientation }));
  addEventListener("error", (e) =>
    log("jserror", { msg: e.message, src: e.filename, line: e.lineno, col: e.colno }));
  addEventListener("unhandledrejection", (e) =>
    log("jsreject", { msg: String(e.reason && (e.reason.stack || e.reason)).slice(0, 500) }));
  document.addEventListener("submit", (e) => {
    const s = e.submitter;
    log("submit", { btn: s ? (s.value || s.name || desc(s)) : null });
    flush(true);
  }, true);

  // --- Tastatur (physisch) ----------------------------------------------
  document.addEventListener("keydown", (e) => {
    log("key", {
      k: e.key, c: e.code,
      m: (e.ctrlKey ? "C" : "") + (e.altKey ? "A" : "") + (e.shiftKey ? "S" : "") + (e.metaKey ? "M" : "") || undefined,
      rep: e.repeat || undefined, tgt: desc(e.target),
    });
  }, true);

  // --- Zeiger: Finger / Stift / Maus ------------------------------------
  // Pro Berührung ein Eintrag beim Loslassen: Dauer, Weg, Anzahl Bewegungen,
  // max. Druck; plus "down" sofort (falls das "up" nie kommt).
  const active = new Map();
  document.addEventListener("pointerdown", (e) => {
    const p = { x: e.clientX, y: e.clientY, t: e.timeStamp, n: 0, pmax: e.pressure || 0, tgt: desc(e.target) };
    active.set(e.pointerId, p);
    log("pdown", { pt: e.pointerType, id: e.pointerId, x: Math.round(e.clientX), y: Math.round(e.clientY),
                   pr: r1(e.pressure || 0), w: r1(e.width || 0), h: r1(e.height || 0),
                   tilt: e.tiltX || e.tiltY ? [e.tiltX, e.tiltY] : undefined,
                   btn: e.button, n: active.size, tgt: p.tgt });
  }, true);
  document.addEventListener("pointermove", (e) => {
    const p = active.get(e.pointerId); if (!p) return;
    p.n++; if (e.pressure > p.pmax) p.pmax = e.pressure;
  }, { capture: true, passive: true });
  function pend(kind) {
    return (e) => {
      const p = active.get(e.pointerId); active.delete(e.pointerId);
      if (!p) { log(kind, { pt: e.pointerType, id: e.pointerId }); return; }
      log(kind, { pt: e.pointerType, id: e.pointerId, ms: Math.round(e.timeStamp - p.t),
                  dx: Math.round(e.clientX - p.x), dy: Math.round(e.clientY - p.y),
                  moves: p.n, prmax: r1(p.pmax), tgt: p.tgt,
                  end: kind === "pup" ? desc(e.target) : undefined });
    };
  }
  document.addEventListener("pointerup", pend("pup"), true);
  document.addEventListener("pointercancel", pend("pcancel"), true);
  document.addEventListener("click", (e) => log("click", { tgt: desc(e.target), x: Math.round(e.clientX), y: Math.round(e.clientY) }), true);
  document.addEventListener("contextmenu", (e) =>
    log("contextmenu", { tgt: desc(e.target), blocked: e.defaultPrevented, pt: e.pointerType || null, x: Math.round(e.clientX), y: Math.round(e.clientY) }), true);

  // --- Formelfeld (MathLive) ---------------------------------------------
  function hookMathfield() {
    const mf = document.getElementById("mf"); if (!mf) return;
    const val = () => { try { return mf.getValue("latex"); } catch (_) { return null; } };
    const sel = () => { try { return mf.selection.ranges; } catch (_) { return null; } };
    mf.addEventListener("focus", () => log("mf.focus"));
    mf.addEventListener("blur", () => log("mf.blur", { v: val() }));
    mf.addEventListener("input", (e) => log("mf.input", { it: e.inputType, d: e.data, v: val(), sel: sel() }));
    let selT = null;   // Auswahländerungen entprellen (Ziehen erzeugt viele)
    mf.addEventListener("selection-change", () => {
      clearTimeout(selT);
      selT = setTimeout(() => log("mf.sel", { sel: sel(), pos: (() => { try { return mf.position; } catch (_) { return null; } })() }), 120);
    });
    // Taucht trotzdem ein MathLive-Menü / Popover auf: protokollieren.
    new MutationObserver((muts) => {
      for (const m of muts) for (const n of m.addedNodes) {
        if (n.nodeType !== 1) continue;
        const c = String(n.className || "") + " " + (n.getAttribute("part") || "");
        if (/ui-menu|popover|ML__/.test(c)) log("ml.popup", { cls: c.trim().slice(0, 80) });
      }
    }).observe(document.body, { childList: true, subtree: false });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", hookMathfield);
  else hookMathfield();

  // --- Bewegung: Schütteln / Stöße ---------------------------------------
  // Beschleunigung ohne Schwerkraft (falls verfügbar), sonst |a_g| - 9.81.
  // Gemeldet wird der Spitzenwert eines 300-ms-Fensters, sobald er die
  // Schwelle überschreitet; Stärke: leicht < 6 ≤ mittel < 15 ≤ stark (m/s²).
  // iOS verlangt dafür eine Erlaubnis (requestPermission) — wird hier nicht
  // angefragt, um keinen Dialog einzublenden; dort fehlen die Daten dann.
  const THRESH = 2.5;
  let peak = 0, winStart = 0, motionSeen = false;
  addEventListener("devicemotion", (e) => {
    let m = null;
    const a = e.acceleration;
    if (a && a.x != null) m = Math.hypot(a.x, a.y, a.z);
    else {
      const g = e.accelerationIncludingGravity;
      if (g && g.x != null) m = Math.abs(Math.hypot(g.x, g.y, g.z) - 9.81);
    }
    if (m == null) return;
    if (!motionSeen) { motionSeen = true; log("motion.available"); }
    const now = Date.now();
    if (m > peak) peak = m;
    if (now - winStart >= 300) {
      if (peak >= THRESH) {
        log("shake", { peak: r1(peak), lvl: peak < 6 ? "leicht" : peak < 15 ? "mittel" : "stark" });
      }
      peak = 0; winStart = now;
    }
  }, { passive: true });

  window.__evlog = { log: log, flush: flush };
})();
