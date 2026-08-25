function normalizeLatex(latex) {
  if (latex == null) return "";
  latex = String(latex);

  latex = latex.replace(/\\left\b/g, "");
  latex = latex.replace(/\\right\b/g, "");

  latex = latex.replace(/\\(?:,|;|quad|qquad)\b/g, " ");

  latex = latex.replace(/\\cdot\b/g, "*");
  latex = latex.replace(/\\times\b/g, "*");

  latex = latex.replace(/\\geqslant\b/g, ">=");
  latex = latex.replace(/\\geq\b/g, ">=");
  latex = latex.replace(/\\leqslant\b/g, "<=");
  latex = latex.replace(/\\leq\b/g, "<=");

  latex = latex.replace(/\\Longleftrightarrow\b/g, " <=> ");
  latex = latex.replace(/\\Leftrightarrow\b/g, " <=> ");
  latex = latex.replace(/\\Longrightarrow\b/g, " => ");
  latex = latex.replace(/\\Rightarrow\b/g, " => ");

  latex = latex.replace(/\\alpha\b/g, "alpha");
  latex = latex.replace(/\\beta\b/g, "beta");
  latex = latex.replace(/\\gamma\b/g, "gamma");
  latex = latex.replace(/\\delta\b/g, "delta");
  latex = latex.replace(/\\varepsilon\b/g, "varepsilon");
  latex = latex.replace(/\\epsilon\b/g, "epsilon");
  latex = latex.replace(/\\lambda\b/g, "lambda");
  latex = latex.replace(/\\mu\b/g, "mu");
  latex = latex.replace(/\\pi\b/g, "pi");
  latex = latex.replace(/\\sigma\b/g, "sigma");
  latex = latex.replace(/\\phi\b/g, "phi");
  latex = latex.replace(/\\varphi\b/g, "varphi");
  latex = latex.replace(/\\omega\b/g, "omega");

  latex = latex.replace(/\\arcsin\b/g, "arcsin");
  latex = latex.replace(/\\arccos\b/g, "arccos");
  latex = latex.replace(/\\arctan\b/g, "arctan");
  latex = latex.replace(/\\sin\b/g, "sin");
  latex = latex.replace(/\\cos\b/g, "cos");
  latex = latex.replace(/\\tan\b/g, "tan");
  latex = latex.replace(/\\ln\b/g, "ln");
  latex = latex.replace(/\\log\b/g, "log");
  latex = latex.replace(/\\exp\b/g, "exp");

  latex = replaceFracOnceRepeatedly(latex);
  latex = replaceSqrtOnceRepeatedly(latex);

  latex = latex.replace(/(\d)\{\s*,\s*\}(\d)/g, "$1.$2");
  latex = latex.replace(/(\d)\s*,\s*(\d)/g, "$1.$2");

  latex = latex.replace(/[ \t\r\n]+/g, " ").trim();
  return latex;
}

function replaceFracOnceRepeatedly(s) {
  var old;
  do {
    old = s;
    s = s.replace(/\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, "(($1)/(($2)))");
  } while (s !== old);
  return s;
}

function replaceSqrtOnceRepeatedly(s) {
  var old;
  do {
    old = s;
    s = s.replace(/\\sqrt\s*\{([^{}]*)\}/g, "sqrt($1)");
  } while (s !== old);
  return s;
}

function splitTextAndMath(latex) {
  var out, i, m, start, depth, j, chunk, content;
  out = [];
  i = 0;

  while (i < latex.length) {
    m = latex.slice(i).match(/^\\(?:textrm|text)\{/);

    if (!m) {
      j = i;
      while (j < latex.length && !latex.slice(j).match(/^\\(?:textrm|text)\{/)) j++;
      chunk = latex.slice(i, j);
      if (chunk.trim() !== "") out.push({ type: "math", value: chunk.trim() });
      i = j;
      continue;
    }

    if (m.index !== 0) {
      chunk = latex.slice(i, i + m.index);
      if (chunk.trim() !== "") out.push({ type: "math", value: chunk.trim() });
      i += m.index;
      continue;
    }

    start = i + m[0].length;
    depth = 1;
    j = start;

    while (j < latex.length && depth > 0) {
      if (latex[j] === "{") depth++;
      else if (latex[j] === "}") depth--;
      j++;
    }

    content = latex.slice(start, j - 1);
    out.push({ type: "text", text: content });
    i = j;
  }

  return out;
}

function splitTopLevelWithSeparators(s, separators) {
  var result, buf, i, depthParen, depthBrace, depthBracket, matched, sep;
  result = [];
  buf = "";
  depthParen = 0;
  depthBrace = 0;
  depthBracket = 0;

  for (i = 0; i < s.length; i++) {
    if (s[i] === "(") depthParen++;
    else if (s[i] === ")") depthParen--;
    else if (s[i] === "{") depthBrace++;
    else if (s[i] === "}") depthBrace--;
    else if (s[i] === "[") depthBracket++;
    else if (s[i] === "]") depthBracket--;

    if (depthParen === 0 && depthBrace === 0 && depthBracket === 0) {
      matched = null;
      for (sep of separators) {
        if (s.slice(i, i + sep.length) === sep) {
          matched = sep;
          break;
        }
      }
      if (matched !== null) {
        result.push({ type: "chunk", value: buf.trim() });
        result.push({ type: "sep", value: matched });
        buf = "";
        i += matched.length - 1;
        continue;
      }
    }

    buf += s[i];
  }

  if (buf.trim() !== "") result.push({ type: "chunk", value: buf.trim() });
  return result;
}

function splitTopLevelSimple(s, separators) {
  return splitTopLevelWithSeparators(s, separators)
    .filter(function(x) { return x.type === "chunk"; })
    .map(function(x) { return x.value; });
}

function stripOuterParens(s) {
  var changed, i, depth;
  s = s.trim();
  changed = true;

  while (changed) {
    changed = false;
    if (s.length >= 2 && s[0] === "(" && s[s.length - 1] === ")") {
      depth = 0;
      changed = true;
      for (i = 0; i < s.length - 1; i++) {
        if (s[i] === "(") depth++;
        else if (s[i] === ")") depth--;
        if (depth === 0 && i < s.length - 2) {
          changed = false;
          break;
        }
      }
      if (changed) s = s.slice(1, -1).trim();
    }
  }

  return s;
}

function isNumberString(s) {
  return /^-?\d+(?:\.\d+)?$/.test(s);
}

function findTopLevelOperator(s, ops, rtl) {
  var i, depthParen, depthBrace, depthBracket, op;
  depthParen = 0;
  depthBrace = 0;
  depthBracket = 0;

  if (rtl) {
    for (i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depthParen++;
      else if (s[i] === "(") depthParen--;
      else if (s[i] === "}") depthBrace++;
      else if (s[i] === "{") depthBrace--;
      else if (s[i] === "]") depthBracket++;
      else if (s[i] === "[") depthBracket--;

      if (depthParen === 0 && depthBrace === 0 && depthBracket === 0) {
        for (op of ops) {
          if (i - op.length + 1 >= 0 && s.slice(i - op.length + 1, i + 1) === op) {
            return { index: i - op.length + 1, op: op };
          }
        }
      }
    }
    return null;
  }

  for (i = 0; i < s.length; i++) {
    if (s[i] === "(") depthParen++;
    else if (s[i] === ")") depthParen--;
    else if (s[i] === "{") depthBrace++;
    else if (s[i] === "}") depthBrace--;
    else if (s[i] === "[") depthBracket++;
    else if (s[i] === "]") depthBracket--;

    if (depthParen === 0 && depthBrace === 0 && depthBracket === 0) {
      for (op of ops) {
        if (s.slice(i, i + op.length) === op) {
          return { index: i, op: op };
        }
      }
    }
  }

  return null;
}

function parseAtom(s) {
  var m, inside, args, fname;

  s = s.trim();
  s = stripOuterParens(s);

  if (s === "") return { type: "empty" };

  if (isNumberString(s)) {
    return { type: "number", value: Number(s) };
  }

  m = s.match(/^([A-Za-z][A-Za-z0-9_]*)\((.*)\)$/);
  if (m) {
    fname = m[1];
    inside = m[2];
    args = splitTopLevelSimple(inside, [",", ";"]).map(function(part) {
      return parseExpr(part);
    });

    return {
      type: "call",
      fn: { type: "symbol", name: fname },
      args: args
    };
  }

  return { type: "symbol", name: s };
}

function parseExpr(s) {
  var hit, left, right;

  s = normalizeLatex(s);
  s = s.trim();
  s = stripOuterParens(s);

  if (s === "") return { type: "empty" };
  if (isNumberString(s)) return { type: "number", value: Number(s) };

  hit = findTopLevelOperator(s, ["+", "-"], true);
  if (hit && hit.index > 0) {
    left = s.slice(0, hit.index);
    right = s.slice(hit.index + hit.op.length);
    return {
      type: "binary",
      op: hit.op,
      left: parseExpr(left),
      right: parseExpr(right)
    };
  }

  hit = findTopLevelOperator(s, ["*", "/"], true);
  if (hit && hit.index > 0) {
    left = s.slice(0, hit.index);
    right = s.slice(hit.index + hit.op.length);
    return {
      type: "binary",
      op: hit.op,
      left: parseExpr(left),
      right: parseExpr(right)
    };
  }

  hit = findTopLevelOperator(s, ["^"], true);
  if (hit && hit.index > 0) {
    left = s.slice(0, hit.index);
    right = s.slice(hit.index + hit.op.length);
    return {
      type: "binary",
      op: "^",
      left: parseExpr(left),
      right: parseExpr(right)
    };
  }

  if (s[0] === "-") {
    return {
      type: "neg",
      arg: parseExpr(s.slice(1))
    };
  }

  return parseAtom(s);
}

function parseRelationChain(s) {
  var tokens, exprs, rels, item, relOps;
  s = normalizeLatex(s);
  relOps = [">=", "<=", "=", ">", "<"];
  tokens = splitTopLevelWithSeparators(s, relOps);

  exprs = [];
  rels = [];

  for (item of tokens) {
    if (item.type === "chunk") exprs.push(parseExpr(item.value));
    else rels.push(item.value);
  }

  if (rels.length === 0) {
    return parseExpr(s);
  }

  return {
    type: "relationChain",
    rels: rels,
    exprs: exprs
  };
}

function parseStepContent(s) {
  return parseRelationChain(s);
}

function parseDerivationMath(latex) {
  var tokens, items, i, chunk, sep, connector;
  latex = normalizeLatex(latex);
  tokens = splitTopLevelWithSeparators(latex, ["<=>", "=>"]);
  items = [];

  for (i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== "chunk") continue;

    chunk = tokens[i].value;
    sep = null;
    connector = null;

    if (i + 1 < tokens.length && tokens[i + 1].type === "sep") {
      sep = tokens[i + 1].value;
      if (sep === "=>") connector = "=>";
      else if (sep === "<=>") connector = "<=>";
    }

    items.push({
      type: "step",
      connectorToNext: connector,
      content: parseStepContent(chunk)
    });
  }

  if (items.length === 1) return items[0].content;

  return {
    type: "derivation",
    items: items
  };
}

function parseMixedAnswer(latex) {
  var parts, items, part, mathAst;
  parts = splitTextAndMath(latex);
  items = [];

  for (part of parts) {
    if (part.type === "text") {
      items.push({
        type: "text",
        text: part.text
      });
    } else {
      mathAst = parseDerivationMath(part.value);

      if (mathAst && mathAst.type === "derivation") {
        items = items.concat(mathAst.items);
      } else {
        items.push({
          type: "step",
          connectorToNext: null,
          content: mathAst
        });
      }
    }
  }

  return {
    type: "derivation",
    items: items
  };
}

function latexAnswerToAST(latex) {
  return parseMixedAnswer(latex);
}