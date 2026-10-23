// Hin-und-zurück-Test für alle Musterlösungen: Maxima → LaTeX (max2tex) → Maxima (mj2max); prüfen mit maxima -b rt.mac
const CE = require(process.env.CE_JS || "/srv/wwwservers/www/tests/html/js/compute-engine.min.umd.js"); const ce = new CE.ComputeEngine();
const mj2max = require("../editor/mj2max.js"), max2tex = require("../editor/max2tex.js"), A = require(require("path").resolve("answers.json")); const L = [];
for (const o of A) {
  let tex, back;
  try { tex = max2tex(o.ta); back = mj2max(ce.parse(tex, { canonical: false }).json); } catch (e) { console.log("ERR", o.id, o.ta, e.message); continue; }
  if (o.id % 15 === 1) console.log(o.id, o.ta, " → ", tex, " → ", back);
  L.push(`print("R", ${o.id}, ratsimp((${o.ta})-(${back})))$`);
}
require("fs").writeFileSync("rt.mac", L.join("\n") + "\n");
