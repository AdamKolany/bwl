// Maxima-Ausdruck (wie ihn mj2max erzeugt) → LaTeX für den bwl-Editor, z. B. (-x^2+2*x*(x-5)-2)/(x-5)^2
// → \frac{-x^2+2x\cdot(x-5)-2}{(x-5)^2}. Läuft im Browser (window.max2tex) und in Node (module.exports).
(function (root) {
  const FUN = { sin: "\\sin", cos: "\\cos", tan: "\\tan", cot: "\\cot", asin: "\\arcsin", acos: "\\arccos", atan: "\\arctan",
    sinh: "\\sinh", cosh: "\\cosh", tanh: "\\tanh", log: "\\ln", exp: "\\exp" };
  const SYM = { "%e": "e", "%pi": "\\pi", "%i": "i", inf: "\\infty" };
  function lex(s) {
    const t = []; let i = 0;
    while (i < s.length) {
      const c = s[i];
      if (/\s/.test(c)) { i++; continue; }
      const m = s.slice(i).match(/^(\d+(\.\d+)?|%?[A-Za-z_][A-Za-z0-9_]*|[-+*/^(),=<>#])/);
      if (!m) throw new Error("Zeichen: " + c);
      t.push(m[0]); i += m[0].length;
    }
    return t;
  }
  // Pratt-Parser → Baum {op, a, b} | {num} | {sym} | {fn, args} | {par}
  function parse(s) {
    const t = lex(s); let p = 0;
    const peek = () => t[p], next = () => t[p++];
    const BP = { "=": 1, "<": 1, ">": 1, "#": 1, "+": 2, "-": 2, "*": 3, "/": 3, "^": 5 };
    function prefix() {
      const k = next();
      if (k === "-") return { op: "neg", a: expr(4) };
      if (k === "+") return expr(4);
      if (k === "(") { const e = expr(0); next(); return { par: e }; }
      if (/^\d/.test(k)) return { num: k };
      if (peek() === "(") { next(); const args = []; if (peek() !== ")") { do { args.push(expr(0)); } while (peek() === "," && next()); } next(); return { fn: k, args }; }
      return { sym: k };
    }
    function expr(min) {
      let l = prefix();
      while (p < t.length && BP[peek()] !== undefined) {
        const o = peek(), bp = BP[o];
        if (bp < min || (bp === min && o !== "^")) break;
        next(); l = { op: o, a: l, b: expr(o === "^" ? bp : bp + 0.5) };
      }
      return l;
    }
    const e = expr(0); if (p < t.length) throw new Error("Rest: " + t.slice(p).join("")); return e;
  }
  const unpar = (e) => (e.par ? unpar(e.par) : e);
  const isAtom = (e) => e.num || e.sym || e.fn;
  function tex(e) {
    if (e.num) return e.num;
    if (e.sym) return SYM[e.sym] || (e.sym.length > 1 ? "\\mathrm{" + e.sym + "}" : e.sym);
    if (e.par) return "(" + tex(e.par) + ")";
    if (e.fn) {
      const a = e.args.map((x) => tex(unpar(x)));
      if (e.fn === "sqrt") return "\\sqrt{" + a[0] + "}";
      if (e.fn === "abs") return "|" + a[0] + "|";
      return (FUN[e.fn] || "\\mathrm{" + e.fn + "}") + "(" + a.join(",") + ")";
    }
    switch (e.op) {
      case "neg": return "-" + tex(e.a);
      case "+": return tex(e.a) + "+" + tex(e.b);
      case "-": return tex(e.a) + "-" + tex(e.b);
      case "*": {
        const l = tex(e.a), r = tex(e.b);
        const b = unpar(e.b);
        // 2*x → 2x, 2*sin(x) → 2\sin(x); sonst \cdot (wie bwl)
        if (e.a.num && (b.sym || b.fn || (b.op === "^" && (b.a.sym || b.a.fn)))) return l + r;
        return l + "\\cdot " + r;
      }
      case "/": return "\\frac{" + tex(unpar(e.a)) + "}{" + tex(unpar(e.b)) + "}";
      case "^": {
        const base = e.a.sym === "%e" ? "e" : (isAtom(e.a) || e.a.par ? tex(e.a) : "(" + tex(e.a) + ")");
        return base + "^{" + tex(unpar(e.b)) + "}";
      }
      default: return tex(e.a) + ({ "#": "\\neq " }[e.op] || e.op) + tex(e.b);
    }
  }
  function max2tex(s) { return tex(parse(s)); }
  if (typeof module !== "undefined") module.exports = max2tex; else root.max2tex = max2tex;
})(this);
