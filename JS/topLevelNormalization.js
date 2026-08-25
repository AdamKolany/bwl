function splitTopLevelCommas(s) {
  const parts = [];
  let depthCurly = 0, depthParen = 0, depthBrack = 0;
  let start = 0;

  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    // pomiń nazwę komendy po backslashu (litery), ale nie pomijaj klamer
    if (ch === "\\") {
      i++;
      while (i < s.length && /[A-Za-z]/.test(s[i])) i++;
      i--;
      continue;
    }

    if (ch === "{") depthCurly++;
    else if (ch === "}") depthCurly = Math.max(0, depthCurly - 1);
    else if (ch === "(") depthParen++;
    else if (ch === ")") depthParen = Math.max(0, depthParen - 1);
    else if (ch === "[") depthBrack++;
    else if (ch === "]") depthBrack = Math.max(0, depthBrack - 1);

    else if (ch === "," && depthCurly === 0 && depthParen === 0 && depthBrack === 0) {
      parts.push(s.slice(start, i).trim());
      start = i + 1;
    }
  }
  parts.push(s.slice(start).trim());  return parts.filter(Boolean);
} // splitTopLevelCommas

function splitTopLevelRelations(s) {
  const parts = []; const rels = [];

  let depthCurly = 0, depthParen = 0, depthBrack = 0; let i = 0, start = 0;

  const cmdRelMap = {
    "\\leqslant": "LessEqual", "\\leq": "LessEqual", "\\le": "LessEqual", "\\geqslant": "GreaterEqual", "\\geq": "GreaterEqual", "\\ge": "GreaterEqual",
    "\\neq": "NotEqual", "\\ne": "NotEqual", "\\approx": "ApproxEqual", "\\sim": "Similar"
  };
  const cmdRels = Object.keys(cmdRelMap);

  while (i < s.length) {
    const ch = s[i];

    if (ch === "\\") {
      let matched = null;
      for (const r of cmdRels) {
        if (s.startsWith(r, i)) {
          const j = i + r.length;
          // granica komendy: po relacji nie może stać litera (żeby \left nie łapało \le)
          if (j >= s.length || !/[A-Za-z]/.test(s[j])) { matched = r; break; }
        }
      }
      if (matched && depthCurly === 0 && depthParen === 0 && depthBrack === 0) {
        parts.push(s.slice(start, i).trim());
        rels.push(cmdRelMap[matched]);
        i += matched.length;
        start = i;
        continue;
      }
      i++; while (i < s.length && /[A-Za-z]/.test(s[i])) i++; continue;
    }

    if (ch === "{") depthCurly++;
    else if (ch === "}") depthCurly = Math.max(0, depthCurly - 1);
    else if (ch === "(") depthParen++;
    else if (ch === ")") depthParen = Math.max(0, depthParen - 1);
    else if (ch === "[") depthBrack++;
    else if (ch === "]") depthBrack = Math.max(0, depthBrack - 1);

    else if ((ch === "=" || ch === "<" || ch === ">") &&
            depthCurly === 0 && depthParen === 0 && depthBrack === 0) {
      parts.push(s.slice(start, i).trim());
      rels.push(ch === "=" ? "Equal" : (ch === "<" ? "Less" : "Greater"));
      i++;
      start = i;
      continue;
    }

    i++;
  }
  parts.push(s.slice(start).trim());
  return { parts: parts.filter(Boolean), rels };
} // splitTopLevelRelations - Ende

function buildRelationChainMathJSON(ce, latex) {
          const { parts, rels } = splitTopLevelRelations(latex);

          if (rels.length === 0) {
            return ce.parse(latex, { form: "raw", canonical: false }).json;
          }

          const nodes = parts.map(p => ce.parse(p, { form: "raw", canonical: false }).json);

          const allSame = rels.every(r => r === rels[0]);
          if (allSame) return [rels[0], ...nodes];

          const chain = ["RelationChain", nodes[0]];
          for (let i = 0; i < rels.length; i++) chain.push(rels[i], nodes[i + 1]);
          return chain;
        } // buildRelationChainMathJSON - Ende

        function parseCommaSeparatedStatements(ce, latex) {
          const chunks = splitTopLevelCommas(latex);
          const nodes = chunks.map(chunk => buildRelationChainMathJSON(ce, chunk));
          return nodes.length === 1 ? nodes[0] : ["Sequence", ...nodes];
        } // parseCommaSeparatedStatements - Ende


function normalizeSumLimits(mj) {
  if (!Array.isArray(mj)) return mj;
  const [op, ...args] = mj.map(normalizeSumLimits);

    if (op === "Sum" && args.length >= 2) {
      const body = args[0];
      const lim = args[1];

      if (Array.isArray(lim) && lim[0] === "Tuple" && lim.length === 4) {
        return ["Sum", body, ["Limits", lim[1], lim[2], lim[3]]];
      }
    }

    if (op === "Product" && args.length >= 2) {
      const body = args[0];
      const lim = args[1];

      if (Array.isArray(lim) && lim[0] === "Tuple" && lim.length === 4) {
        return ["Product", body, ["Limits", lim[1], lim[2], lim[3]]];
      }
    }

    if (op === "Integrate" && args.length >= 2) {
      const body = args[0];
      const lim = args[1];

      if (Array.isArray(lim) && lim[0] === "Tuple" && lim.length === 4) {
        return ["Integrate", body, ["Limits", lim[1], lim[2], lim[3]]];
      }
    }

  return [op, ...args];
  
} // normalizeSumLimits - Ende

function relationChainToSequence(chain) {
  if (!Array.isArray(chain) || chain[0] !== "RelationChain") return chain;

  const items = chain.slice(1);
  if (items.length < 3) return chain;

  const steps = [];
  let left = items[0];

  for (let i = 1; i < items.length; i += 2) {
    const rel = items[i];
    const right = items[i + 1];
    if (right === undefined) break;
    steps.push([rel, left, right]);
    left = right;
  }

  return ["Sequence", ...steps];
} // relationChainToSequence - Ende


