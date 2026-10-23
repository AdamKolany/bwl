// answers.tsv (Export aus der DB bwl, siehe export.sh) → answers.json: Musterlösung und Aufgabenformel als Maxima.
// Aufruf im Arbeitsverzeichnis (Daten liegen dort, nicht im Repo): node <repo>/STACK/gemeinsam/aufgaben/conv.js
const CE = require(process.env.CE_JS || "/srv/wwwservers/www/tests/html/js/compute-engine.min.umd.js"); const ce = new CE.ComputeEngine();
const mj2max = require("../editor/mj2max.js"); const fs = require("fs");
const out = [];
for (const l of fs.readFileSync("answers.tsv", "utf8").trim().split("\n")) {
  const [id, th, tex, hint, q] = l.split("\t");
  let t = tex.replace(/^\s*I\s*=/, "");                       // „I=…“ – Präfix steht schon im Hinweis
  if (th === "unint") t = t.replace(/\+\s*C\s*$/, "");         // Integrationskonstante prüft STACK selbst (ATInt)
  let m = (q.match(/\\\[(.*?)\\\]/) || [])[1] || "";         // erste Formel der Aufgabe
  const ii = m.match(/\\int\s*(.*?)\\?,?\s*d\s*x/); if (ii) m = ii[1];   // Integrand
  let qmax = ""; try { const rhs = m.replace(/^.*?=/, ""); qmax = mj2max(ce.parse(rhs, { canonical: false }).json); } catch (e) { qmax = "ERR " + e.message; }
  let a; try { a = mj2max(ce.parse(t, { canonical: false }).json); } catch (e) { a = "ERR " + e.message; }
  let extra = {};
  if (th === "pldiv") {                                        // P(x)=… \text{~~und~~} S(x)=…
    const f2 = (q.match(/\\\[(.*?)\\\]/g) || [])[1] || "";
    const pm = f2.match(/P\(x\)=(.*?)\\text/), sm = f2.match(/S\(x\)=(.*?)\\\]/);
    try { extra = { P: mj2max(ce.parse(pm[1], { canonical: false }).json), S: mj2max(ce.parse(sm[1], { canonical: false }).json) }; } catch (e) { extra = { P: "ERR", S: "ERR" }; }
  }
  out.push({ id: +id, th, tex, hint, q, ta: a, qexpr: qmax, ...extra });
}
fs.writeFileSync("answers.json", JSON.stringify(out, null, 1));
for (const o of out) console.log(o.id, o.th, o.ta, " | ", o.qexpr);
