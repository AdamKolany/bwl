

  function cmd_romgr(mf) {
    if (mf.selectionIsCollapsed !== false) return;
    const sel = mf.selection; const s = (mf.getValue ? (mf.getValue(sel, "latex") || "") : ""); if (!s) return; const repl = toGreekLatex(s);  mf.executeCommand("insert", repl);
  }
  
  function toGreekLatex(ch) {
   const lower = {
     a: "\\alpha", b: "\\beta",  g: "\\gamma",  c: "\\chi", d: "\\delta",    z: "\\zeta",    e: "\\eta",    
     t: "\\vartheta", i: "\\iota",  k: "\\kappa",  l: "\\lambda",   m: "\\mu",      n: "\\nu",
     x: '\\xi',    p: "\\pi",    r: "\\varrho", s: "\\varsigma", y: "\\upsilon", f: "\\varphi", c: "\\chi",  };
   const upper = { 
     G: "\\Gamma", D: "\\Delta", C: "\\Chi", T: "\\Theta", L: "\\Lambda", X: "\\Xi", P: "\\Pi", S: "\\Sigma", U: "\\Upsilon", F: "\\Phi", Y: "\\Psi", O: "\\Omega",  };

     if (ch >= "a" && ch <= "z") return lower[ch] ?? ch; if (ch >= "A" && ch <= "Z") return upper[ch] ?? ch; return ch; 
  }

