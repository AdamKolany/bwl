// Weitere bwl-Formelaufgaben (alle DBs außer der Umfrage-Aufgabenauswahl) → items.json + alle.mac (Maxima rechnet/prüft).
// Eingabe: uniq.tsv aus export_alle.sh (db, frage_id, kapitel, thema, th_kürzel, antwort_latex, hint, frage).
// Wo die DB keine reine Endlösung enthält (Vorlagen „…=“, Rechenwege), rechnet Maxima die Musterlösung aus der Aufgabe.
// Aufruf im Arbeitsverzeichnis: node <repo>/STACK/gemeinsam/aufgaben/alle.js && maxima --very-quiet -b alle.mac > alle.out
const CE = require(process.env.CE_JS || "/srv/wwwservers/www/tests/html/js/compute-engine.min.umd.js"); const ce = new CE.ComputeEngine();
const mj2max = require("../editor/mj2max.js"); const fs = require("fs");
const prep = (t) => t.replace(/\\[,;!]/g, " ").replace(/\\left|\\right/g, "")
  .replace(/\\(sin|cos|tan|ln)\s*([a-z])(?![a-zA-Z{(])/g, "\\$1($2)")   // \cos x\sqrt{…} → \cos(x)\sqrt{…}
  .replace(/\\(ln|sin|cos)\^(\d)\s*\(?([a-z])\)?/g, "(\\$1($3))^$2")    // \ln^3x → (\ln(x))^3
  .replace(/\\\\+$/, "").trim();
const tex2max = (t) => mj2max(ce.parse(prep(t), { canonical: false }).json);
// LaTeX-Token lesen: {…} (ausgeglichen), \befehl oder ein Zeichen
function tok(s, i) {
  if (s[i] === "{") { let d = 0, j = i; for (; j < s.length; j++) { if (s[j] === "{") d++; if (s[j] === "}" && --d === 0) break; } return [s.slice(i + 1, j), j + 1]; }
  if (s[i] === "\\") { const m = s.slice(i).match(/^\\[a-zA-Z]+/); return [m[0], i + m[0].length]; }
  return [s[i], i + 1];
}
const first = (q) => ((q.match(/\\\[(.*?)\\\]/) || q.match(/\\\((.*?)\\\)/) || [])[1] || "").trim();
const BWLTH = { abltn: 1, stamf: 1, unint: 1, dopbr: 1, pldiv: 1, ausml: 1, auskl: 1, brtrm: 1 };
const items = [], skipped = {};
const skip = (r, why) => { (skipped[r.thema] = skipped[r.thema] || {})[why] = ((skipped[r.thema] || {})[why] || 0) + 1; };
for (const l of fs.readFileSync("uniq.tsv", "utf8").split("\n")) {
  if (!l.trim()) continue;
  const [db, id, kap, thema, th, tex, hint, q] = l.split("\t");
  const r = { db, id: +id, kap: (kap || "").trim(), thema: (thema || "").trim(), th, tex, hint: (hint || "").trim(), q };
  const f = first(q);
  try {
    if (BWLTH[th]) {                                            // wie Umfrage: Endlösung steht in der DB
      let t = tex.replace(/^\s*I\s*=/, ""); if (th === "unint") t = t.replace(/\+\s*C\s*$/, "");
      r.kind = th; r.ta = tex2max(t);
      const m = f.replace(/^.*?=/, ""); const ii = f.match(/\\int\s*(.*?)\\?,?\s*d\s*\\?!?\s*x/);
      if (th === "pldiv") {
        const f2 = (q.match(/\\\[(.*?)\\\]/g) || [])[1] || f;
        r.P = tex2max(f2.match(/P\(x\)=(.*?)(\\\\|\\text|\\quad|,|$)/)[1]); r.S = tex2max(f2.match(/S\(x\)=(.*?)(\\\]|$)/)[1]);
      } else if (th === "stamf") { r.check = tex2max(m); }
      else r.check = tex2max(ii ? ii[1] : m);
    } else if (/\\int/.test(f)) {
      let i = f.indexOf("\\int") + 4, lo, hi;
      while (f[i] === " ") i++;
      if (f[i] === "_") { [lo, i] = tok(f, i + 1); while (f[i] === " ") i++; }
      if (f[i] === "^") { [hi, i] = tok(f, i + 1); }
      let body = f.slice(i).trim(), v = "x";
      const fr = body.match(/^\\frac\{d([a-z])\}/);
      if (fr) { v = fr[1]; body = body.replace(/^\\frac\{d[a-z]\}/, "\\frac{1}"); }
      else { const dm = body.match(/(?:\\,|\\;|\s)*(?:\\mathrm\{d\}|\\mathcal\{d\}|d)\s*\\?!?\s*([a-z])\s*$/); if (dm) { v = dm[1]; body = body.slice(0, dm.index); } }
      r.v = v; r.f = tex2max(body);
      if (lo !== undefined) { r.kind = "bestint"; r.a = tex2max(lo); r.b = tex2max(hi); } else r.kind = "int";
      r.hint = "\\mathcal{I}=";
    } else if (/\\lim/.test(f)) {
      const m = f.match(/\\lim_\{?\s*([a-z])\s*\\to\s*([^}]*?)\}\s*(.*)$/);
      r.kind = "lim"; r.v = m[1]; r.p = /infty/.test(m[2]) ? "inf" : tex2max(m[2]); r.f = tex2max(m[3]); r.hint = "\\mathcal{G}=";
    } else if (/\\sum/.test(f)) {
      const m = f.match(/\\sum_\{\s*([a-z])\s*=\s*(\d+)\s*\}\^\{?\\infty\}?\s*(.*)$/);
      r.kind = "sum"; r.v = m[1]; r.n0 = +m[2]; r.f = tex2max(m[3]); r.hint = "\\mathcal{S}=";
    } else if (/^Rechne im Kopf/.test(q) && !/\\text|circ|%|\\%|von/.test(f)) {
      const e = f.replace(/=\s*$/, "").replace(/(\d)\s*\{,\}\s*(\d)/g, "$1.$2").replace(/:/g, "\\div ");
      r.kind = "kopf"; r.f = tex2max(e); r.hint = f.replace(/=\s*$/, "") + "=";
    } else { skip(r, "keine eindeutige Einzellösung"); continue; }
  } catch (e) { skip(r, "nicht lesbar: " + String(e.message).slice(0, 40)); continue; }
  items.push(r);
}
// Maxima: Musterlösung berechnen (ta) und gegenprüfen (R = 0 heißt in Ordnung)
const L = ["display2d: false$", "simpsum: true$", "load(\"simplify_sum\")$"];
const P = (it, ta, chk) => L.push(`(ta: ${ta}, print("T", ${it.id}, "${it.db}", string(ta)), print("R", ${it.id}, "${it.db}", ${chk}))$`);
for (const it of items) {
  switch (it.kind) {
    case "int": P(it, `integrate(${it.f}, ${it.v})`, `ratsimp(trigsimp(diff(ta, ${it.v}) - (${it.f})))`); break;
    case "bestint": P(it, `block([r: ratsimp(integrate(${it.f}, ${it.v}, ${it.a}, ${it.b}))], if freeof(sin, cos, r) then r else ratsimp(trigsimp(trigreduce(r))))`, `if abs(float(ta) - quad_qags(${it.f}, ${it.v}, ${it.a}, ${it.b})[1]) < 1e-8 then 0 else "num"`); break;
    case "lim": P(it, `limit(${it.f}, ${it.v}, ${it.p})`, `if member(ta, [und, ind, infinity]) or not freeof(nounify(limit), ta) then "lim" else 0`); break;
    case "sum": P(it, `simplify_sum(sum(${it.f}, ${it.v}, ${it.n0}, inf))`, `if abs(float(ta) - float(sum(${it.f}, ${it.v}, ${it.n0}, 400))) < 1e-8 then 0 else "sum"`); break;
    case "kopf": P(it, `ratsimp(${it.f})`, `0`); break;
    case "abltn": P(it, it.ta, `ratsimp(diff(${it.check}, x) - (ta))`); break;
    case "stamf": case "unint": P(it, it.ta, `ratsimp(diff(ta, x) - (${it.check}))`); break;
    case "pldiv": P(it, it.ta, `ratsimp(divide(${it.P}, ${it.S}, x)[${it.hint.startsWith("R") ? 2 : 1}] - (ta))`); break;
    default: P(it, it.ta, `ratsimp((${it.check}) - (ta))`); L.push(`print("F", ${it.id}, "${it.db}", string(ratsimp(${it.check})))$`);
  }
}
fs.writeFileSync("alle.mac", L.join("\n") + "\n");
fs.writeFileSync("items.json", JSON.stringify(items, null, 1));
console.log("Aufgaben:", items.length); console.log("übersprungen:", JSON.stringify(skipped, null, 1));
