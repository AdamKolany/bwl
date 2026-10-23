// MathJSON (Compute Engine) → Maxima-Syntax für STACK. Läuft im Browser (window.mj2max) und in Node (module.exports).
(function (root) {
  const FUN = { Sin: "sin", Cos: "cos", Tan: "tan", Cot: "cot", Sec: "sec", Csc: "csc", Arcsin: "asin", Arccos: "acos",
    Arctan: "atan", Sinh: "sinh", Cosh: "cosh", Tanh: "tanh", Ln: "log", Exp: "exp", Abs: "abs", Floor: "floor", Ceil: "ceiling" };
  const SYM = { ExponentialE: "%e", Pi: "%pi", ImaginaryUnit: "%i", PositiveInfinity: "inf", NegativeInfinity: "minf" };
  const REL = { Equal: "=", Less: "<", LessEqual: "<=", Greater: ">", GreaterEqual: ">=", NotEqual: "#" };
  const P = { add: 1, mul: 2, neg: 2, pow: 4, atom: 9 };          // Bindungsstärke
  function num(x) { return x < 0 ? { s: String(x), p: P.neg } : { s: String(x), p: P.atom }; }
  function wrap(e, p) { return e.p < p ? "(" + e.s + ")" : e.s; }
  function conv(x) {
    if (typeof x === "number") return num(x);
    if (typeof x === "string") {
      if (x in SYM) return { s: SYM[x], p: P.atom };
      if (/^-?\d+(\.\d+)?$/.test(x)) return num(Number(x));
      return { s: x.replace(/[^A-Za-z0-9_]/g, ""), p: P.atom };
    }
    if (x && typeof x === "object" && !Array.isArray(x)) {
      if ("num" in x) return num(Number(x.num)); if ("sym" in x) return conv(x.sym); if ("fn" in x) return conv(x.fn);
    }
    if (!Array.isArray(x) || !x.length) throw new Error("unbekannt: " + JSON.stringify(x));
    const [op, ...a] = x;
    switch (op) {
      case "Delimiter": return conv(a[0]);
      case "Add": {
        let s = "";
        a.forEach((t, i) => {
          const neg = Array.isArray(t) && t[0] === "Negate";
          const e = conv(neg ? t[1] : t);
          if (i === 0) s = neg ? "-" + wrap(e, P.mul) : wrap(e, P.add);
          else if (neg) s += "-" + wrap(e, P.mul);
          else if (e.s.startsWith("-")) s += "-" + wrap({ s: e.s.slice(1), p: e.p === P.neg ? P.atom : e.p }, P.mul);
          else s += "+" + wrap(e, P.add);
        });
        return { s, p: P.add };
      }
      case "Subtract": return conv(["Add", a[0], ["Negate", a[1]]]);
      case "Negate": { const e = conv(a[0]); return { s: "-" + (e.p >= P.mul ? e.s : "(" + e.s + ")"), p: P.neg }; }
      case "Multiply": case "InvisibleOperator": {
        if (typeof a[0] === "number" && a[0] < 0 && a.length > 1) {   // -7*x statt (-7)*x
          const r = a[0] === -1 ? a.slice(1) : [-a[0], ...a.slice(1)];
          return { s: "-" + r.map(t => wrap(conv(t), P.mul + 0.5)).join("*"), p: P.neg };
        }
        return { s: a.map(t => wrap(conv(t), P.mul + 0.5)).join("*"), p: P.mul };
      }
      case "Divide": return { s: wrap(conv(a[0]), P.mul) + "/" + wrap(conv(a[1]), P.mul + 0.5), p: P.mul };
      case "Rational": return { s: wrap(conv(a[0]), P.mul) + "/" + wrap(conv(a[1]), P.mul + 0.5), p: P.mul };
      case "Power":
        if (a[0] === "ExponentialE") return { s: "%e^" + wrap(conv(a[1]), P.atom), p: P.pow };
        return { s: wrap(conv(a[0]), P.pow + 0.5) + "^" + wrap(conv(a[1]), P.atom), p: P.pow };
      case "Square": return conv(["Power", a[0], 2]);
      case "Sqrt": return { s: "sqrt(" + conv(a[0]).s + ")", p: P.atom };
      case "Root": return { s: wrap(conv(a[0]), P.pow + 0.5) + "^(1/" + wrap(conv(a[1]), P.atom) + ")", p: P.pow };
      case "Log": return a.length > 1 ? { s: "log(" + conv(a[0]).s + ")/log(" + conv(a[1]).s + ")", p: P.mul } : { s: "log(" + conv(a[0]).s + ")/log(10)", p: P.mul };
      default:
        if (op in REL) return { s: a.map(t => conv(t).s).join(REL[op]), p: 0 };
        if (op in FUN) return { s: FUN[op] + "(" + a.map(t => conv(t).s).join(",") + ")", p: P.atom };
        throw new Error("nicht unterstützt: " + op);
    }
  }
  function mj2max(json) { return conv(json).s; }
  if (typeof module !== "undefined") module.exports = mj2max; else root.mj2max = mj2max;
})(this);
