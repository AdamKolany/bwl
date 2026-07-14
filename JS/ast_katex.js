/* ast_katex.js
 * KaTeX parse tree -> czytelne AST (bez semantyki CE, bez typów).
 * Wymaga: katex (katex.min.js) już załadowany.
 */

(function () {
  // ------- helpers: pretty printer -------
function pretty(ast, indent = 0, maxInline = 100) {
  const sp = "  ".repeat(indent);
  function inline(x) {
    if (x == null) return "null";
    if (typeof x === "string" || typeof x === "number") return String(x);
    if (!Array.isArray(x)) return JSON.stringify(x);
    const op = x[0];
    const args = x.slice(1);
    // liście: Symbol/Number w jednej linii
    if (op === "Symbol" || op === "Number") {
      return `${op}(${args.map(inline).join(", ")})`;
    }
    // jednoargumentowe proste w jednej linii
    if (args.length <= 2) {
      return `${op}(${args.map(inline).join(", ")})`;
    }
    return `${op}(${args.map(inline).join(", ")})`;
  }

  function multi(x, ind) {
    const sp2 = "  ".repeat(ind);

    if (x == null) return sp2 + "null";
    if (typeof x === "string" || typeof x === "number") return sp2 + String(x);
    if (!Array.isArray(x)) return sp2 + JSON.stringify(x);

    const one = inline(x);
    if (one.length <= maxInline) return sp2 + one;

    const op = x[0];
    const args = x.slice(1);

    // specjalnie: Sequence i RelationChain czytelniej
    if (op === "Sequence" || op === "RelationChain") {
      let out = sp2 + op + "(\n";
      out += args.map(a => multi(a, ind + 1)).join(",\n");
      out += "\n" + sp2 + ")";
      return out;
    }

    // reszta
    let out = sp2 + op + "(\n";
    out += args.map(a => multi(a, ind + 1)).join(",\n");
    out += "\n" + sp2 + ")";
    return out;
  }

  return multi(ast, indent);
} // pretty

  // ------- KaTeX parse tree -> token stream -------
  // token: {k:"sym"|"num"|"op"|"rel"|"comma"|"lpar"|"rpar"|"ast", v:any}
  function push(out, k, v) { out.push({ k, v }); }

  const RELMAP = {
    "=": "Equal",
    "\\le": "LessEqual", "\\leq": "LessEqual", "\\leqslant": "LessEqual",
    "\\ge": "GreaterEqual", "\\geq": "GreaterEqual", "\\geqslant": "GreaterEqual",
    "\\approx": "ApproxEqual", "\\sim": "Similar",
    "\\ne": "NotEqual", "\\neq": "NotEqual",
    "<": "Less", ">": "Greater"
  };

  function isDigitStr(s) { return /^[0-9]+(\.[0-9]+)?$/.test(s); }

  function nodeText(n) {
    // KaTeX nodes różnie przechowują tekst
    if (!n) return "";
    if (typeof n === "string") return n;
    if (n.text) return n.text;
    if (typeof n.value === "string") return n.value;
    if (typeof n.name === "string") return n.name;
    if (typeof n.label === "string") return n.label;
    return "";
  }

  function walkNode(n, out) {
    if (n == null) return;

    if (Array.isArray(n)) { for (const x of n) walkNode(x, out); return; }

    const t = n.type;

    // grupy / styling -> tylko body
    if (t === "ordgroup" || t === "styling" || t === "color" || t === "size") {
      walkNode(n.body, out);
      return;
    }

    // nawiasy \left...\right
    if (t === "leftright") {
      push(out, "lpar", n.left || "(");
      walkNode(n.body, out);
      push(out, "rpar", n.right || ")");
      return;
    }

    // ułamek
    if (t === "genfrac" || t === "frac") {
      const num = tokensToAST(tokensFromNode(n.numer));
      const den = tokensToAST(tokensFromNode(n.denom));
      push(out, "ast", ["Divide", num, den]);
      return;
    }

    // sqrt
    if (t === "sqrt") {
      const arg = tokensToAST(tokensFromNode(n.body));
      push(out, "ast", ["Sqrt", arg]);
      return;
    }

    // supsub (potęga/indeks)
    if (t === "supsub") {
      const base = tokensToAST(tokensFromNode(n.base));
      if (n.sup && !n.sub) {
        const exp = tokensToAST(tokensFromNode(n.sup));
        push(out, "ast", ["Power", base, exp]);
        return;
      }
      if (n.sub && !n.sup) {
        const sub = tokensToAST(tokensFromNode(n.sub));
        push(out, "ast", ["Sub", base, sub]);
        return;
      }
      // oba: zachowaj surowo
      const sup = n.sup ? tokensToAST(tokensFromNode(n.sup)) : null;
      const sub = n.sub ? tokensToAST(tokensFromNode(n.sub)) : null;
      push(out, "ast", ["SupSub", base, sup, sub]);
      return;
    }

    // operator funkcji: \sin, \cos, \ln, \exp, ...
    if (t === "op" || t === "mathop") {
      const name = nodeText(n) || (n.name ? String(n.name) : "");
      // push(out, "sym", "\\" + name.replace(/^\\/, ""));
      push(out, "sym", name.replace(/^\\/, ""));
      return;
    }

    // przecinek
    if (t === "punct") {
      const tx = nodeText(n);
      if (tx === "," || tx === "\\," || tx === "\\;") { push(out, "comma", ","); return; }
    }

    // relacje i operatory binarne (KaTeX często koduje jako atom/rel/bin)
    if (t === "atom" || t === "rel" || t === "bin") {
      const tx = nodeText(n);
      if (tx === ",") { push(out, "comma", ","); return; }

      if (RELMAP[tx]) { push(out, "rel", RELMAP[tx]); return; }

      // jawne znaki + - = < >
      if (tx === "+" || tx === "-" || tx === "*" || tx === "/" || tx === "=" || tx === "<" || tx === ">") {
        if (tx === "=" || tx === "<" || tx === ">") push(out, "rel", RELMAP[tx]);
        else push(out, "op", tx);
        return;
      }
    }

    // zwykłe symbole/liczby
    if (t === "mathord" || t === "textord") {
      const tx = nodeText(n);
      if (!tx) return;

      // nawiasy zwykłe (czasem wchodzą jako textord)
      if (tx === "(") { push(out, "lpar", "("); return; }
      if (tx === ")") { push(out, "rpar", ")"); return; }

      if (tx === ",") { push(out, "comma", ","); return; }

      if (isDigitStr(tx)) { push(out, "num", Number(tx)); return; }

      // operatory
      if (tx === "+" || tx === "-" || tx === "*" || tx === "/") { push(out, "op", tx); return; }
      if (tx === "=" || tx === "<" || tx === ">") { push(out, "rel", RELMAP[tx]); return; }

      push(out, "sym", tx);
      return;
    }

    // fallback: jeśli node ma body -> wejdź
    if (n.body) { walkNode(n.body, out); return; }
  }

  function tokensFromNode(node) {
    const out = [];
    walkNode(node, out);
    return out;
  }

  // ------- token stream -> AST (Pratt / shunting-yard hybrid) -------
  function tokensToAST(tokens) {
    // 1) split by top-level commas -> Sequence
    const parts = [];
    let cur = [];
    let depth = 0;
    for (const tk of tokens) {
      if (tk.k === "lpar") depth++;
      if (tk.k === "rpar") depth = Math.max(0, depth - 1);

      if (tk.k === "comma" && depth === 0) {
        parts.push(cur);
        cur = [];
        continue;
      }
      cur.push(tk);
    }
    parts.push(cur);

    const nodes = parts.map(parseRelationChain);
    if (nodes.length === 1) return nodes[0];
    return ["Sequence", ...nodes];
  }

  function parseRelationChain(tokens) {
    // split by top-level rel -> RelationChain
    const segs = [];
    const rels = [];

    let cur = [];
    let depth = 0;
    for (const tk of tokens) {
      if (tk.k === "lpar") depth++;
      if (tk.k === "rpar") depth = Math.max(0, depth - 1);

      if (tk.k === "rel" && depth === 0) {
        segs.push(cur);
        rels.push(tk.v);
        cur = [];
        continue;
      }
      cur.push(tk);
    }
    segs.push(cur);

    const exprs = segs.map(parseExpr);
    if (rels.length === 0) return exprs[0];

    const out = ["RelationChain", exprs[0]];
    for (let i = 0; i < rels.length; i++) out.push(rels[i], exprs[i + 1]);
    return out;
  }

  function parseExpr(tokens) {
    // Shunting-yard for +,-,*,/ and implicit multiplication; power already AST in tokens (via supsub)
    const output = [];
    const ops = [];

    function prec(op) {
      if (op === "u-") return 5;
      if (op === "*" || op === "/") return 4;
      if (op === "+" || op === "-") return 3;
      return 0;
    }
    function applyOp(op) {
      if (op === "u-") {
        const a = output.pop();
        output.push(["Negate", a]);
        return;
      }
      const b = output.pop();
      const a = output.pop();
      if (op === "+") output.push(["Add", a, b]);
      else if (op === "-") output.push(["Subtract", a, b]);
      else if (op === "*") output.push(["Multiply", a, b]);
      else if (op === "/") output.push(["Divide", a, b]);
    }

    // helper: implicit multiplication between two atoms
    function isAtomTok(tk) {
      return tk && (tk.k === "sym" || tk.k === "num" || tk.k === "ast" || tk.k === "rpar");
    }
    function isAtomStart(tk) {
      return tk && (tk.k === "sym" || tk.k === "num" || tk.k === "ast" || tk.k === "lpar");
    }

    let prev = null;

    for (let i = 0; i < tokens.length; i++) {
      const tk = tokens[i];

      // inject implicit multiplication
      if (prev && isAtomTok(prev) && isAtomStart(tk)) {
        // treat as *
        while (ops.length && prec(ops[ops.length - 1]) >= prec("*")) applyOp(ops.pop());
        ops.push("*");
      }

      if (tk.k === "num") output.push(["Number", tk.v]);
      else if (tk.k === "sym") output.push(["Symbol", tk.v]);
      else if (tk.k === "ast") output.push(tk.v);
      else if (tk.k === "lpar") ops.push("(");
      else if (tk.k === "rpar") {
        while (ops.length && ops[ops.length - 1] !== "(") applyOp(ops.pop());
        if (ops.length && ops[ops.length - 1] === "(") ops.pop();
      } else if (tk.k === "op") {
        const op = tk.v;
        // unary minus
        if (op === "-" && (!prev || (prev.k === "op" || prev.k === "lpar" || prev.k === "rel"))) {
          ops.push("u-");
        } else {
          while (ops.length && prec(ops[ops.length - 1]) >= prec(op)) applyOp(ops.pop());
          ops.push(op);
        }
      }

      prev = tk;
    }

    while (ops.length) {
      const op = ops.pop();
      if (op === "(") continue;
      applyOp(op);
    }

    // function application: Symbol followed by Paren-group appears as implicit multiplication in this simple version.
    // W praktyce: użytkownik chce Apply(f, x) dla f(x).
    // Tu naprawiamy najczęstszy wzorzec: Multiply(Symbol(f), Paren(expr)) -> Apply(Symbol(f), expr)
    return rewriteApply(output[0]);
  }

  function rewriteApply(ast) {
    if (!Array.isArray(ast)) return ast;
    const op = ast[0];

    const rec = (x) => rewriteApply(x);

    if (op === "Multiply" && ast.length === 3) {
      const a = rec(ast[1]);
      const b = rec(ast[2]);

      // Apply: Symbol * Paren(expr)  -> Apply(Symbol, expr)
      if (Array.isArray(a) && a[0] === "Symbol" && Array.isArray(b) && b[0] === "Paren") {
        return ["Apply", a, rec(b[1])];
      }
      return ["Multiply", a, b];
    }

    if (op === "Paren") return ["Paren", rec(ast[1])];

    return [op, ...ast.slice(1).map(rec)];
  }

function rewritePrimes(ast) {
  if (!Array.isArray(ast)) return ast;

  // przejdź rekurencyjnie
  const op = ast[0];
  const args = ast.slice(1).map(rewritePrimes);

  // przypadek: Power(Symbol(f), Symbol("'")) albo Power(Symbol(f), Symbol("\\prime"))
  if (op === "Power" && args.length === 2) {
    const base = args[0], exp = args[1];

    const isPrime =
      Array.isArray(exp) && exp[0] === "Symbol" &&
      (exp[1] === "'" || exp[1] === "\\prime");

    if (isPrime) return ["Prime", base];
    return ["Power", base, exp];
  }

  // jeśli już masz Prime node’y – zostaw
  return [op, ...args];
  }

  // ------- public API -------
  function latexToPrettyAST(latex) {
    if (!window.katex || ! katex.__parse) throw new Error("KaTeX not loaded");
    const tree = katex.__parse(latex);
    const tokens = tokensFromNode(tree);
    const ast = rewritePrimes(tokensToAST(tokens));
    return pretty(ast);
  }

  // expose
  window.latexToPrettyAST = latexToPrettyAST;
})();
