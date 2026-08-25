function prettyMathJSON(mj, opts = {}) {
  const maxInline = opts.maxInline ?? 90;
  const indentStr = opts.indentStr ?? "  ";

  const relSym = {
    LessEqual: "≤",
    Less: "<",
    GreaterEqual: "≥",
    Greater: ">",
    Equal: "=",
    NotEqual: "≠",
    ApproxEqual: "≈",
    Similar: "∼"
  };

  function isAtom(x) {
    return x === null || x === undefined ||  typeof x === "number" || typeof x === "string";
  } // isAtom

  function inline(x) {
    if (x === null || x === undefined) return String(x);
    if (typeof x === "number") return String(x);
    if (typeof x === "string") return x;
    if (!Array.isArray(x) || x.length === 0) return String(x);

    const op = x[0];

    // Negate
    if (op === "Negate" && x.length === 2) {
      const t = inline(x[1]);
      return (isAtom(x[1]) ? `-${t}` : `-(${t})`);
    }

    // RelationChain inline
    if (op === "RelationChain") {
      let i = 1, meta = null;
      if (typeof x[i] === "number") { meta = x[i]; i++; }
      const first = inline(x[i++]);
      const pieces = [first];
      while (i < x.length) {
        const rel = x[i++]; const node = x[i++];
        pieces.push(relSym[rel] ?? rel, inline(node));
      }
      const head = meta !== null ? `RelationChain(meta=${meta}, ` : "RelationChain(";
      return head + pieces.join(" ") + ")";
    }

    const args = x.slice(1).map(inline);
    return `${op}(${args.join(", ")})`;
  } // inLine

  function multiline(x, depth) {
    const sp = indentStr.repeat(depth);

    if (isAtom(x)) return sp + String(x);
    if (!Array.isArray(x) || x.length === 0) return sp + String(x);

    const op = x[0];

    // Negate
    if (op === "Negate" && x.length === 2) {
      const tInline = inline(x);
      if (tInline.length <= maxInline) return sp + tInline;
      return sp + "-(\n" + multiline(x[1], depth + 1) + "\n" + sp + ")";
    }

    // RelationChain pretty
    if (op === "RelationChain") {
      let i = 1, meta = null;
      if (typeof x[i] === "number") { meta = x[i]; i++; }

      const firstNode = x[i++];

      // try inline
      const one = inline(x);
      if (one.length <= maxInline) return sp + one;

      let out = sp + (meta !== null ? `RelationChain(meta=${meta},\n` : "RelationChain(\n");
      out += multiline(firstNode, depth + 1);

      while (i < x.length) {
        const rel = x[i++]; const node = x[i++];
        const sym = relSym[rel] ?? rel;
        out += ",\n" + indentStr.repeat(depth + 1) + sym + ", ";
        const nodeInline = inline(node);
        if (nodeInline.length <= maxInline / 2) {
          out += nodeInline;
        } else {
          out += "\n" + multiline(node, depth + 2);
        }
      }

      out += "\n" + sp + ")";
      return out;
    }

    // Sequence: always multiline (unless short)
    if (op === "Sequence") {
      const one = inline(x);
      if (one.length <= maxInline) return sp + one;

      const items = x.slice(1);
      let out = sp + "Sequence(\n";
      out += items.map(it => multiline(it, depth + 1)).join(",\n");
      out += "\n" + sp + ")";
      return out;
    }

    // regular operators: inline if short
    const one = inline(x);
    if (one.length <= maxInline) return sp + one;

    const args = x.slice(1);
    let out = sp + op + "(\n";
    out += args.map(a => multiline(a, depth + 1)).join(",\n");
    out += "\n" + sp + ")";
    return out;
  }

  return multiline(mj, 0);
} // end of PrettyMathJSON

  function showPrettyMathJSON(outMJ,mjDialog,mjPre) {

    let txt = "";  
    try {    
      const mj = JSON.parse(outMJ.value || "null");    
      txt = prettyMathJSON(mj);  
    } catch (e) { txt = "Nie mogę sparsować user_mathjson jako JSON.\n"+e+"\n" + (outMJ.value || "");  }
    
    if (mjDialog && mjDialog.showModal) { mjPre.textContent = txt;  mjDialog.showModal();  } else { alert(txt); }

  } // showPrettyMathJSON - Ende

  function prettyPrimes(latex) {
    return latex
      .replace(/\^\{\\prime\\prime\\prime\}/g, "'''")
      .replace(/\^\{\\prime\\prime\}/g, "''")
      .replace(/\^\{\\prime\}/g, "'")
      .replace(/\^\\prime/g, "'");
  } // prettyPrimes

  function prettyPrimesForDisplay(latex) {
    return latex
      .replace(/\^\{\\prime\\prime\\prime\}/g, "\u2034")
      .replace(/\^\{\\prime\\prime\}/g, "\u2033")
      .replace(/\^\{\\prime\}/g, "\u2032")
      .replace(/\^\\prime/g, "\u2032");
  } // prettyPrimesForDisplay

/* */
  function refreshDebugMirrors(ltx,outLatex,mjs,outMJ) {
    if (ltx && outLatex) {    ltx.textContent = prettyPrimesForDisplay(outLatex.value || "");  }
    if (mjs && outMJ) { const v = outMJ.value || "";  mjs.textContent = v .replace(/"/g, "") .replace(/,/g, ",") .replace(/(\[\|\])/g, "\u200a$1\u200a"); }
  } // refreshDebugMirrors - Ende  
/* */

/* */
  function cleanupLatex(latex) {
    if (!latex) return latex;
    
    return latex
      .replace(/_\{\s*\}/g, "")
      .replace(/_\{\s*\\,\s*\}/g, "")
      .replace(/\^\{\s*\}/g, "")
      .replace(/\^\{\s*\\,\s*\}/g, "")
      //.replace(/\\(:,|;|:|!|quad|qquad| )/g, "")
      ;
  } // cleanupLatex - Ende
/* */

/* */
  
const _cleaning = {p: false};

function cleanMathfieldInPlace() {
  if (_cleaning.p) return;  _cleaning.p = true;
  try { 
    const raw = mf.getValue("latex") || ""; const cleaned = cleanupLatex(raw); 
    if (cleaned !== raw) { mf.setValue(cleaned, { format: "latex", suppressChangeNotifications: true }); } 
  } finally { _cleaning.p = false; }
} // cleanMathfieldInPlace - Ende
/* */

