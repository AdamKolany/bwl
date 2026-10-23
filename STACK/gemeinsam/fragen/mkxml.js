// Moodle-XML mit STACK-Fragen aus den bwl-Aufgaben (Aufgabenauswahl = verbindlicher Satz), Antwort über den bwl-Editor
const A = require(require("path").resolve("answers.json")), fs = require("fs");
const { question, category, prt, THEMA } = require("./stackxml.js");
let x = `<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n`;
for (const th of Object.keys(THEMA)) {
  x += category(`bwl-Aufgabenauswahl/${THEMA[th]}`);
  for (const o of A.filter((o) => o.th === th)) {
    x += question(o, prt(th), { name: THEMA[th] + " " + o.id, idnumber: "bwl-" + o.id,
      muster: "<p>Musterlösung: \\(" + o.hint.trim() + " " + o.tex.replace(/^\s*I\s*=/, "") + "\\)</p>",
      testvalue: o.th === "unint" ? "ta+c" : "ta" });
  }
}
x += "</quiz>\n";
fs.writeFileSync("bwl-stack.xml", x); console.log(x.length, "Bytes,", (x.match(/type="stack"/g) || []).length, "Fragen");
