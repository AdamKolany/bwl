// Brücke bwl-Editor → STACK: liest den bereinigten LaTeX-Text, den DOMContentLoaded.js in #user_latex schreibt,
// rechnet ihn über MathJSON in Maxima-Syntax um und schickt ihn an die umgebende STACK-[[iframe]].
// Gesendet wird erst nach einer Änderung durch den Nutzer – sonst würde der leere Editor beim Neuladen
// die gespeicherte Antwort überschreiben. Eine gespeicherte Antwort (Maxima) wird mit max2tex.js in den Editor zurückgeholt.
(function () {
  const qs = new URLSearchParams(location.search);
  const hint = qs.get("hint") || "";
  const mf = document.getElementById("mf");
  if (mf) mf.textContent = hint ? hint + " " : "";              // Präfix wie in bwl, z. B. f'(x)=
  const evlog = (typ, d) => { try { if (window.__evlog) window.__evlog.log(typ, d); } catch (_) {} };
  // Kontext fürs Ereignisprotokoll: Frage (idnumber) und Moodle-Versuch/Slot (STACK-quid „q<usage>:<slot>_…“)
  evlog("moodle", { q: qs.get("q") || null, ctx: qs.get("ctx") || null, hint });
  let last = null, ce = null;
  function toMaxima(latex) {
    let t = latex.trim();
    if (hint && t.includes("=")) t = t.slice(t.indexOf("=") + 1);  // Präfix „f'(x)=“ abschneiden
    t = t.replace(/(\d)\s*(?:\{,\}|,)\s*(\d)/g, "$1.$2");      // Dezimalkomma: 4,85 → 4.85
    t = t.replace(/(\d)\s*e(?![a-zA-Z])/g, "$1\\cdot e");          // 4e+1 ist 4·e+1, nicht 4·10¹ (Compute Engine liest sonst Exponentialschreibweise)
    t = t.replace(/\\[,;:! ]/g, " ").trim();
    if (!t) return "";
    ce = ce || new ComputeEngine.ComputeEngine();
    return mj2max(ce.parse(t, { canonical: false }).json);
  }
  function current() { const el = document.getElementById("user_latex"); return el ? el.value || "" : null; }
  function send() {
    const latex = current();
    if (latex === null || !window.ComputeEngine || !window.mj2max) return;
    if (last === null) { last = latex; return; }                  // Ausgangszustand merken, nicht senden
    if (latex === last) return; last = latex;
    let maxima = "", err = "";
    try { maxima = toMaxima(latex); } catch (e) { err = String(e.message || e); }
    const st = document.getElementById("stackStatus");
    if (st) st.textContent = err ? "unvollständig" : maxima;
    evlog("stack.answer", { latex, maxima, err: err || undefined });
    parent.postMessage(JSON.stringify({ type: "bwl-answer", maxima, latex, err }), "*");
  }
  setInterval(send, 300);
  let lastH = 0;                                                  // Höhe melden, damit die STACK-iframe mitwächst
  setInterval(() => { const bx = document.querySelector(".box"); const h = Math.ceil((bx ? bx.getBoundingClientRect().bottom : document.body.scrollHeight) + 6); if (Math.abs(h - lastH) > 4) { lastH = h; parent.postMessage(JSON.stringify({ type: "bwl-height", h }), "*"); } }, 500);
  // gespeicherte Maxima-Antwort → LaTeX (max2tex.js), z. B. (2*x-7)*%e^(x^2-7*x) → (2x-7)\cdot e^{x^{2}-7x}
  function restore(maxima) {
    if (!mf || !mf.setValue || !window.max2tex) return false;
    let tex = ""; if (maxima) { try { tex = max2tex(maxima); } catch (_) { return true; } }   // unvollständig: Editor lassen
    mf.setValue((hint ? hint + " " : "") + tex);
    evlog("stack.restore", { maxima, tex });
    last = null;                                                  // wiederhergestellter Stand = neuer Ausgangszustand
    return true;
  }
  addEventListener("message", (e) => {
    let d; try { d = JSON.parse(e.data); } catch (_) { return; }
    if (d && d.type === "bwl-restore" && typeof d.maxima === "string") {
      const tryIt = (n) => { if (!restore(d.maxima) && n > 0) setTimeout(() => tryIt(n - 1), 300); };
      tryIt(20);
    }
  });
  parent.postMessage(JSON.stringify({ type: "bwl-ready" }), "*");
})();
