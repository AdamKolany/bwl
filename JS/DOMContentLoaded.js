document.addEventListener ( "DOMContentLoaded", () => {
        const mf = document.getElementById("mf");
        const mjs = document.getElementById("mjs");
        const ltx = document.getElementById("ltx");
        const ast = document.getElementById("ast");

        const ltxLink  = document.getElementById("ltx_link");
        const mjsLink  = document.getElementById("mjs_link");
        const astLink  = document.getElementById("ast_link");

        const mjDialog = document.getElementById("mj_dialog");
        
        const mjPre    = document.getElementById("mj_pre");
        const mjClose  = document.getElementById("mj_close");

        const outLatex = document.getElementById("user_latex"); 
        const outMJ    = document.getElementById("user_mathjson");

        if (!mf) return;  // mf.isFunction = (name) => name === "f" || name === "g";

        mf.mathVirtualKeyboardPolicy = "off"; // mf.virtualKeyboardMode = "off";  // Do not remove !!
      
        if (!MathfieldElement.computeEngine && window.ComputeEngine) { MathfieldElement.computeEngine = new ComputeEngine.ComputeEngine(); }

        const ce = MathfieldElement.computeEngine; if (!ce) { console.error("ComputeEngine missing"); return; }

        let ltxval= outLatex.value;  ltx.textContent = prettyPrimes(ltxval);
        //let mjsval= outMJ.value;     mjs.textContent = 'wait';// mjsval.replace(/"/g,'').replace(/,/g,' , ').replace(/(\[\|\])/g," \$1 ");
        
        
        mf.addEventListener("blur", cleanMathfieldInPlace);

  
        if (!window.__ceDeclaredFG) {
            window.__ceDeclaredFG = true;  
            const decl = { f: "(number)->number", g: "(number)->number", h: "(number)->number", /* np. p: "(number, number)->number" */ };
            for (const [name, sig] of Object.entries(decl)) { try { ce.declare(name, sig); } catch (_) {}  }
        }

        ( function patchMathLiveHighlight() {
            if (!mf || !mf.shadowRoot) return;

            const css = `
            .ML__contains-highlight{
              opacity: 0.05 !important;
              background: rgba(255,255,0,1) !important;
            }`;

            // nie dubluj
            if (mf.shadowRoot.getElementById("ml-highlight-fix")) return;

            const st = document.createElement("style");
            st.id = "ml-highlight-fix";
            st.textContent = css;
            mf.shadowRoot.appendChild(st);
          } 
        ) ();

  function replaceInvisibleOperator(node) {
    if (Array.isArray(node)) {
      const mapped = node.map(replaceInvisibleOperator);
      if (mapped[0] === 'InvisibleOperator') { return ['Multiply', ...mapped.slice(1)]; } return mapped;
    }
    if (node && typeof node === 'object') {
      const out = {};
      for (const [k, v] of Object.entries(node)) { out[k] = replaceInvisibleOperator(v); } return out;
    }
    return node;
  }

  function normalizeMJ(node) {
    if (Array.isArray(node)) {
      let xs = node.map(normalizeMJ);

      if (xs[0] === "InvisibleOperator") {
        xs = ["Multiply", ...xs.slice(1)];
      }

      if (xs[0] === "Delimiter" && xs.length === 2) {
        return xs[1];
      }

      if (xs[0] === "Add" || xs[0] === "Multiply") {
        const head = xs[0];
        const args = [];
        for (const t of xs.slice(1)) {
          if (Array.isArray(t) && t[0] === head) args.push(...t.slice(1));
          else args.push(t);
        }
        xs = [head, ...args];
      }

      return xs;
    }

    if (node && typeof node === "object") {
      const out = {};
      for (const [k, v] of Object.entries(node)) out[k] = normalizeMJ(v);
      return out;
    }

    return node;
  }

  function sameStructure(a, b) {
    return JSON.stringify(normalizeMJ(a)) === JSON.stringify(normalizeMJ(b));
  }

  function mjSize(node) {
    if (Array.isArray(node)) {
      return 1 + node.reduce((s, x) => s + mjSize(x), 0);
    }
    if (node && typeof node === "object") {
      return 1 + Object.values(node).reduce((s, x) => s + mjSize(x), 0);
    }
    return 1;
  }

  let localClipLatex = "";

  const update = () => {

    // 1) latex — zawsze
    const raw = (mf && mf.getValue) ? (mf.getValue("latex-unstyled") || mf.getValue("latex") || mf.getValue("latex-expanded") || "") : "";
  
    const latex0 = cleanupLatex(raw);

    if (outLatex) outLatex.value = latex0;

    answer = document.getElementById("answer"); if (answer) latex1 = answer.getAttribute("data-answer");
    
    /* 
    // 2) LTX podgląd — zawsze
    try {
      if (ltx) ltx.textContent = 'LTX:\n\t'+latex0 + "\n\t------------------------------------\n\t" + latex1; // prettyPrimesForDisplay ? prettyPrimesForDisplay(latex0) : latex0;
    } catch (e) { if (ltx) ltx.textContent = latex0; }
    /* */

    // 3) MJS — osobno TUTAJ
    try {
      const mj = parseCommaSeparatedStatements(MathfieldElement.computeEngine, latex0);
      if (outMJ) outMJ.value = JSON.stringify(replaceInvisibleOperator(mj));
      if (mjs) {

        const CE = new window.ComputeEngine.ComputeEngine(); 
        const json0 = replaceInvisibleOperator(CE.parse(latex0, { form: 'raw'} ).json[2]);
        const json1 = replaceInvisibleOperator(CE.parse(latex1, { form: 'raw'} ).json);
        
        const json0c = CE.box(normalizeMJ(json0)).canonical 
        const json1c = CE.box(normalizeMJ(json1)).canonical 
        
        const diff = CE.box(["Subtract", json0c.json, json1c.json]).simplify();
        const j1 = JSON.stringify( json0 ).replace(/\"/g,"");
        const result = diff.isEqual(0);

       /* Vorübergehend 
        mjs.textContent = 'MJS: \n\t'+'[STD: '+(mjSize(json0))+']\t→\t'+JSON.stringify( json0 ).replace(/\"/g,"") + 
                          "\n\t------------------------------------------------------------------\n\t" +
                          '[ANT: '+(mjSize(json1))+']\t→\t'+JSON.stringify( json1 ).replace(/\"/g,"") + 
                          "\n\t------------------------------------------------------------------\n\t" +  result 
        ;
        /* */

        document.getElementById('richtig').value = diff.isEqual(0) ? 'J' : 'N';
        const s1=document.getElementById('score');
        s1.dataset.score = diff.isEqual(0) ? 1 : 0;
        /* Vorübergehend 
        s1.textContent = (result === undefined) ? "" : (diff.isEqual(0) ? " [Richtig]" : " [Falsch]");
        /* */
      }
    } catch (e) {
      if (outMJ) outMJ.value = "";
      if (mjs) mjs.textContent = "MJS error";
    }

    /*
    // 4) AST — osobno (NIGDY nie może zabić update)
    try {
      if (ast) {
        if (window.latexToPrettyAST) ast.textContent = window.latexToPrettyAST(latex0); else ast.textContent = "AST parser not loaded";
      }
    } catch (e) { if (ast) ast.textContent = "AST error"; }
    /* */

    /*  
    const thema = document.getElementById("thema");
    if ( thema.value !== "") {
      const start=document.getElementById("test-start"); if (start) start.disabled = false;
    }
    /* */

  }; // update

  mf.addEventListener("input", update);


  const handlePbtn = (e) => {
      const btn = e.target.closest(".pbtn"); if (!btn) return; try { mf.focus(); } catch(_) {}
      const cmd = btn.getAttribute("data-cmd") || "";  const ins = btn.getAttribute("data-ins") || ""; try { mf.focus(); } catch(_) {}

      // od tego miejsca to są nasze przyciski-palety:
      e.preventDefault();
      e.stopPropagation();

      if (cmd === "bs"        ) { try { mf.executeCommand("deleteBackward"); update(); } catch (_) {} return; }
      if (cmd === "del"       ) { try { mf.executeCommand("deleteForward");  update(); } catch (_) {} return; }
      if (cmd === "undo"      ) { try { mf.executeCommand("undo");           update(); } catch (_) {} return; }
      if (cmd === "redo"      ) { try { mf.executeCommand("redo");           update(); } catch (_) {} return; }
      if (cmd === "clear"     ) { try {  if (mf.selectionIsCollapsed === false) { mf.executeCommand("insert", ""); update(); } } catch (_) {}  return; }
      if (cmd === "selectAll" ) { try { mf.executeCommand("selectAll"); update(); } catch (_) {} return; }
      if (cmd === "move_L"    ) { try { mf.executeCommand("moveToPreviousChar"); update(); } catch(_) {} return; }
      if (cmd === "move_R"    ) { try { mf.executeCommand("moveToNextChar");     update(); } catch(_) {} return; }

      if (cmd === "capsel"    ) {
        try {
          if (mf.selectionIsCollapsed !== false) return;
          const sel = mf.selection;
          const s = (mf.getValue ? (mf.getValue(sel, "latex") || "") : "");
          const c = s[0];
          if (c >= "a" && c <= "z") mf.executeCommand("insert", c.toUpperCase());
          else if (c >= "A" && c <= "Z") mf.executeCommand("insert", c.toLowerCase());
          update();
        } catch (_) {}
        return;
      } // cmd="capsel"

      if (cmd === "romgr") { try { cmd_romgr(mf); } catch (err) { console.error("romgr failed:", err); }  update();  return; }

      if (cmd === "copy") {
        try {
          if (mf.selectionIsCollapsed !== false) { localClipLatex = mf.getValue("latex") || ""; return; }
          const sel = mf.selection;  localClipLatex = (mf.getValue(sel, "latex") || ""); } catch (err) { console.error("copy failed:", err); }
        return;
      } // cmd === "copy"

      if (cmd === "paste") { 
        try { 
              if (!localClipLatex) return; 
              mf.executeCommand("insert", localClipLatex); mf.focus(); update(); 
            } catch (err) { console.error("paste failed:", err); } 
        return; 
      } //cmd = "paste"

      function tryCmd(mf, name) { try { mf.executeCommand(name); return true; } catch(e) { return false; } } 

      if (cmd === "selL") {  try { mf.executeCommand("extendToPreviousWord"); } catch (_) {}  update(); return; }
      if (cmd === "selR") {  try { mf.executeCommand("extendToNextWord");     } catch (_) {}  update(); return; }
      if (ins) { try { mf.executeCommand("insert", ins); update(); } catch (_) {} }  try { mf.focus(); } catch(_) {} };

      // nie pozwól, żeby klik w pbtn zabierał focus (focus zostaje w math-field)
      document.addEventListener ( 
        "pointerdown", (e) => { const btn = e.target.closest(".pbtn"); if (!btn) return;  e.preventDefault(); try { mf.focus(); } catch(_) {}  }, true 
      );

      document.addEventListener("click", handlePbtn, true);

      const form = mf.closest("form"); if (form) form.addEventListener ( "submit" , () => { try { update(); } catch (e) {} } );

      window.addEventListener ( "load" ,  () => { if (window.MathfieldElement && window.ComputeEngine) { MathfieldElement.computeEngine = new ComputeEngine.ComputeEngine(); } } ); 

      update();

  }
); // Ende von Listener: DOMContentLoaded
