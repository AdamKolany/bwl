// Maxima-Batch: prüft jede umgerechnete Musterlösung gegen die Aufgabe
const A = require(require("path").resolve("answers.json")); const L = [];
for (const o of A) {
  let t;
  switch (o.th) {
    case "abltn": t = `ratsimp(diff(${o.qexpr},x)-(${o.ta}))`; break;
    case "stamf": case "unint": t = `ratsimp(diff(${o.ta},x)-(${o.qexpr}))`; break;
    case "pldiv": t = `ratsimp(divide(${o.P},${o.S},x)[${o.hint.startsWith("R") ? 2 : 1}]-(${o.ta}))`; break;
    default: t = `ratsimp(${o.qexpr}-(${o.ta}))`;
  }
  L.push(`print("R", ${o.id}, ${t})$`);
}
require("fs").writeFileSync("check.mac", L.join("\n") + "\n");
