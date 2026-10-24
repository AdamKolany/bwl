// Gemeinsame Bausteine für STACK-Fragen im Moodle-XML-Format (auch vom ILIAS-STACK-Plugin importierbar):
// Fragetext mit eingebettetem bwl-Editor, PRT-Knoten, Fragegerüst. Benutzt von mkxml.js (bwl) und mkalle.js (Testmaterial).
const EDITOR = process.env.STACKBWL_EDITOR || "http://mathe-c10-mua.inw.hs-merseburg.de/stackbwl/editor.html";   // andere Plattform/Host: hier umstellen
const THEMA = { abltn: "Ableitungen", stamf: "Stammfunktionen", unint: "Unbestimmte Integrale", dopbr: "Doppelbrüche",
  pldiv: "Polynomdivision", ausml: "Ausmultiplizieren", auskl: "Ausklammern", brtrm: "Bruchterme" };
const cd = (s) => "<![CDATA[" + String(s).replace(/\]\]>/g, "]]]]><![CDATA[>") + "]]>";
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function node(n, test, sans, tans, opts, T, F) {
  return `      <node><name>${n}</name><description></description><answertest>${test}</answertest><sans>${esc(sans)}</sans><tans>${esc(tans)}</tans>
        <testoptions>${esc(opts)}</testoptions><quiet>0</quiet>
        <truescoremode>=</truescoremode><truescore>${T.score}</truescore><truepenalty></truepenalty><truenextnode>${T.next}</truenextnode><trueanswernote>prt1-${n + 1}-T</trueanswernote>
        <truefeedback format="html"><text>${cd(T.fb || "")}</text></truefeedback>
        <falsescoremode>=</falsescoremode><falsescore>${F.score}</falsescore><falsepenalty></falsepenalty><falsenextnode>${F.next}</falsenextnode><falseanswernote>prt1-${n + 1}-F</falseanswernote>
        <falsefeedback format="html"><text>${cd(F.fb || "")}</text></falsefeedback></node>\n`;
}
function prt(th, v) {
  const ok = { score: 1, next: -1 }, no = { score: 0, next: -1 };
  switch (th) {
    case "unint": return { fv: "", nodes: node(0, "Int", "ans1", "ta", "x", ok, no), note: "prt1-1-T" };
    case "ausml": return { fv: "", note: "prt1-2-T", nodes: node(0, "AlgEquiv", "ans1", "ta", "", { score: 1, next: 1 }, no) +
        node(1, "Expanded", "ans1", "ta", "", ok, { score: 0.5, next: -1, fb: "Richtig, aber noch nicht vollständig ausmultipliziert." }) };
    case "auskl": return { fv: "istprod: is(not atom(ans1) and member(op(ans1), [\"*\", \"^\", \"-\"]));", note: "prt1-2-T",
        nodes: node(0, "AlgEquiv", "ans1", "ta", "", { score: 1, next: 1 }, no) +
        node(1, "AlgEquiv", "istprod", "true", "", ok, { score: 0.5, next: -1, fb: "Richtig, aber nicht ausgeklammert (kein Produkt)." }) };
    case "brtrm": return { fv: "", note: "prt1-2-T", nodes: node(0, "AlgEquiv", "ans1", "ta", "", { score: 1, next: 1 }, no) +
        node(1, "SingleFrac", "ans1", "ta", "", ok, { score: 0.5, next: -1, fb: "Richtig, aber nicht als ein einziger Bruch geschrieben." }) };
    case "int": return { fv: "", nodes: node(0, "Int", "ans1", "ta", v || "x", ok, no), note: "prt1-1-T" };
    case "kopf": return { fv: "", nodes: node(0, "NumAbsolute", "ans1", "ta", "0.000001", ok, no), note: "prt1-1-T" };
    default: return { fv: "", nodes: node(0, "AlgEquiv", "ans1", "ta", "", ok, no), note: "prt1-1-T" };
  }
}
function qtext(o) {
  const hint = o.hint.trim();
  const q = o.q.replace(/\\text\{~~und~~\}/g, "\\quad\\text{und}\\quad ");
  return `<p>${q}</p>
[[iframe width="100%" height="560px" title="bwl-Formeleditor"]]
[[style]] html, body { margin: 0; padding: 0; overflow: hidden; } #bwled { border: 0; width: 100%; height: 552px; display: block; } [[/style]]
<iframe id="bwled" src="${EDITOR}?hint=${encodeURIComponent(hint)}&q=${encodeURIComponent(o.idnumber || "")}&ctx=[[quid id='log'/]]"></iframe>
<a href="#" id="txtlink" style="font: 13px sans-serif; color: #0f6cbf; margin-left: 4px;">Texteingabe ▾</a>
<script type="module">
import stack_js from '[[cors src="stackjsiframe.min.js"/]]';
const ed = document.getElementById("bwled"); let inp = null, ready = false, restored = false;
const restore = () => { if (inp && ready && !restored) { restored = true; if (inp.value) ed.contentWindow.postMessage(JSON.stringify({ type: "bwl-restore", maxima: inp.value }), "*"); } };
let fromEditor = null, opened = false;
const TXT = "[[quid id='txt'/]]";
const showTxt = () => stack_js.toggle_visibility(TXT, opened);   // nur auf Wunsch (Link „Texteingabe“)
showTxt();
document.getElementById("txtlink").addEventListener("click", (e) => { e.preventDefault(); opened = !opened; showTxt(); });
stack_js.request_access_to_input("ans1", true).then((id) => {
  inp = document.getElementById(id); restore(); showTxt();
  // Eingabe im Textfeld (die alte Art) → Editor nachziehen
  inp.addEventListener("change", () => { if (ready && inp.value !== fromEditor) ed.contentWindow.postMessage(JSON.stringify({ type: "bwl-restore", maxima: inp.value }), "*"); showTxt(); });
});
window.addEventListener("message", (e) => {
  if (e.source !== ed.contentWindow) return;
  let d; try { d = JSON.parse(e.data); } catch (_) { return; }
  if (d.type === "bwl-ready") { ready = true; restore(); }
  if (d.type === "bwl-answer" && inp && inp.value !== d.maxima) { fromEditor = d.maxima; inp.value = d.maxima; inp.dispatchEvent(new Event("change")); showTxt(); }
  if (d.type === "bwl-height") { ed.style.height = d.h + "px"; stack_js.resize_containing_frame("100%", (d.h + 28) + "px"); }
});
</script>
[[/iframe]]
<div id="[[quid id='txt'/]]"><p>Texteingabe (Maxima): [[input:ans1]]</p></div>
[[validation:ans1]]`;
}
// o: {q, hint, ta}; p: prt(…); z: {name, idnumber, muster, decimals, forbidfloat, testvalue}
function question(o, p, z) {
  o = Object.assign({}, o, { idnumber: z.idnumber });
  return `<question type="stack">
  <name><text>${esc(z.name)}</text></name>
  <questiontext format="html"><text>${cd(qtext(o))}</text></questiontext>
  <generalfeedback format="html"><text>${cd(z.muster)}</text></generalfeedback>
  <defaultgrade>1</defaultgrade><penalty>0.1</penalty><hidden>0</hidden><idnumber>${esc(z.idnumber)}</idnumber>
  <stackversion><text>2026101500</text></stackversion>
  <questionvariables><text>${cd("ta: " + o.ta + ";")}</text></questionvariables>
  <specificfeedback format="html"><text>[[feedback:prt1]]</text></specificfeedback>
  <questionnote><text></text></questionnote><questiondescription format="html"><text></text></questiondescription>
  <questionsimplify>1</questionsimplify><assumepositive>0</assumepositive><assumereal>0</assumereal>
  <decimals>${z.decimals || ","}</decimals><multiplicationsign>dot</multiplicationsign><sqrtsign>1</sqrtsign><complexno>i</complexno><inversetrig>cos-1</inversetrig><logicsymbol>lang</logicsymbol><matrixparens>[</matrixparens>
  <variantsselectionseed></variantsselectionseed>
  <input><name>ans1</name><type>algebraic</type><tans>ta</tans><boxsize>40</boxsize><strictsyntax>1</strictsyntax><insertstars>0</insertstars>
    <syntaxhint></syntaxhint><syntaxattribute>0</syntaxattribute><forbidwords></forbidwords><allowwords></allowwords><forbidfloat>${z.forbidfloat === 0 ? 0 : 1}</forbidfloat>
    <requirelowestterms>0</requirelowestterms><checkanswertype>0</checkanswertype><mustverify>0</mustverify><showvalidation>1</showvalidation><options></options></input>
  <prt><name>prt1</name><value>1.0000000</value><autosimplify>1</autosimplify><feedbackstyle>1</feedbackstyle>
    <feedbackvariables><text>${cd(p.fv)}</text></feedbackvariables>
${p.nodes}  </prt>
  <qtest><testcase>1</testcase><description>Musterlösung</description><testinput><name>ans1</name><value>${cd(z.testvalue || "ta")}</value></testinput>
    <expected><name>prt1</name><expectedscore>1.0000000</expectedscore><expectedpenalty>0.0000000</expectedpenalty><expectedanswernote>${p.note}</expectedanswernote></expected></qtest>
</question>\n`;
}
const category = (path) => `<question type="category"><category><text>$course$/top/${path}</text></category></question>\n`;
module.exports = { cd, esc, node, prt, qtext, question, category, THEMA, EDITOR };
