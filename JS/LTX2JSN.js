function rewriteInvisibleApply(expr) {
  if (Array.isArray(expr)) {
    const head = expr[0];
    const args = expr.slice(1).map(rewriteInvisibleApply);

    if (
      head === "InvisibleOperator" &&
      args.length === 2 &&
      Array.isArray(args[1]) &&
      args[1][0] === "Delimiter"
    ) {
      const inside = args[1][1];

      if (Array.isArray(inside) && inside[0] === "Sequence") {
        return ["Apply", args[0], ...inside.slice(1)];
      }

      return ["Apply", args[0], inside];
    }

    return [head, ...args];
  }

  if (expr && typeof expr === "object") {
    const out = {};
    for (const [k, v] of Object.entries(expr)) {
      out[k] = rewriteInvisibleApply(v);
    }
    return out;
  }

  return expr;
}

function normalizeSequenceDelimiters(expr) {
  if (Array.isArray(expr)) {
    const head = expr[0];
    const args = expr.slice(1).map(normalizeSequenceDelimiters);

    if (head === "Delimiter" && args.length === 1) {
      return args[0];
    }

    if (head === "Sequence") {
      return [
        "Sequence",
        ...args.filter(x => x !== "," && x !== ";")
      ];
    }

    return [head, ...args];
  }

  if (expr && typeof expr === "object") {
    const out = {};
    for (const [k, v] of Object.entries(expr)) {
      out[k] = normalizeSequenceDelimiters(v);
    }
    return out;
  }

  return expr;
}

function cleanMathJSON(expr) {
  return normalizeSequenceDelimiters(rewriteInvisibleApply(expr));
}

function latexToCleanMathJSON(ce, latex) {
  const expr = ce.parse(latex, { form: "raw" });
  return cleanMathJSON(expr.json);
}

function extractSequenceItems(expr) {
  const cleaned = cleanMathJSON(expr);
  if (Array.isArray(cleaned) && cleaned[0] === "Sequence") {
    return cleaned.slice(1);
  }
  return [cleaned];
}

function latexToSequenceItems(ce, latex) {
  const cleaned = latexToCleanMathJSON(ce, latex);
  if (Array.isArray(cleaned) && cleaned[0] === "Sequence") {
    return cleaned.slice(1);
  }
  return [cleaned];
}

