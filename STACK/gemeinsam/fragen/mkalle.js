// Testmaterial (alte Sätze henning/julia/abitur/drak, NICHT verbindlich) → bwl-stack-alle.xml
// Eingabe im Arbeitsverzeichnis: items.json (alle.js) und alle.out (maxima -b alle.mac: T = Musterlösung, R = Prüfung, F = aus der Aufgabe berechnet)
const fs = require("fs"), path = require("path");
const { question, category, prt } = require("./stackxml.js");
const max2tex = require("../editor/max2tex.js");
const items = require(path.resolve("items.json"));
const T = {}, R = {}, F = {};
for (const l of fs.readFileSync("alle.out", "utf8").split("\n")) {
  const m = l.match(/^([TRF]) (\d+) (\w+) (.*?)\s*$/); if (!m) continue;
  ({ T, R, F })[m[1]][m[3] + "-" + m[2]] = m[4];
}
// Fragetext: $…$ → \(…\), \\ außerhalb von Formeln → Zeilenumbruch
function fixq(q) {
  return q.split(/(\\\[.*?\\\]|\\\(.*?\\\))/).map((seg, i) => i % 2 ? seg
    : seg.replace(/\$([^$]+)\$/g, "\\($1\\)").replace(/\\\\(?![a-zA-Z])/g, "<br>")).join("");
}
const groups = {}, report = { ok: 0, korrigiert: [], fehlt: [] };
for (const it of items) {
  const key = it.db + "-" + it.id; let ta = T[key];
  if (!ta || R[key] === undefined) { report.fehlt.push(key); continue; }
  if (R[key] !== "0") {
    if (F[key] !== undefined) { report.korrigiert.push(`${key}: DB ${ta} → ${F[key]}`); ta = F[key]; }
    else { report.fehlt.push(key + " (Prüfung " + R[key] + ")"); continue; }
  }
  const grp = (it.kap || it.db) + "/" + it.thema;
  (groups[grp] = groups[grp] || []).push({ it, ta });
}
let x = `<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n`, n = 0;
for (const grp of Object.keys(groups).sort()) {
  x += category("Testmaterial (alt)/" + grp);
  for (const { it, ta } of groups[grp]) {
    const kind = it.kind === "int" || it.kind === "unint" ? "int" : it.kind;
    const plusC = kind === "int" ? "+C" : "";
    let muster; try { muster = max2tex(ta); } catch (_) { muster = ta; }
    const o = { q: fixq(it.q), hint: it.hint || "", ta };
    x += question(o, prt(it.kind === "int" ? "int" : it.kind, it.v), {
      name: `${it.thema} ${it.db}-${it.id}`, idnumber: `${it.db}-${it.id}`,
      muster: "<p>Musterlösung: \\(" + (it.hint || "") + " " + muster + plusC + "\\)</p>",
      decimals: it.kind === "kopf" ? "." : ",", forbidfloat: it.kind === "kopf" ? 0 : 1,
      testvalue: kind === "int" ? "ta+c" : "ta" });
    n++; report.ok++;
  }
}
x += "</quiz>\n";
fs.writeFileSync("bwl-stack-alle.xml", x);
console.log(n, "Fragen in", Object.keys(groups).length, "Themen"); console.log(JSON.stringify(report, null, 1));
