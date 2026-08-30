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

        // Wyłącz wbudowane skróty MathLive (np. "u"→∪, "@"→∘) — litery wpisywane
        // fizyczną klawiaturą mają zostawać literami (zmiennymi), nie zamieniać się w symbole.
        try { mf.inlineShortcuts = {}; } catch (_) {}
      
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

  // Zeichenlimit: zählt "sinnvolle" Länge, nicht rohe LaTeX-Länge —
  // leere Platzhalter zählen nicht. Die meisten LaTeX-Befehle stehen für
  // EIN Symbol (\int, \alpha, \sum, ...) und zählen als 1 Zeichen; die
  // ausgeschriebenen Funktionsnamen (\sin, \arcsin, ...) stehen dagegen
  // für so viele Zeichen, wie sie Buchstaben haben (\sin = 3, wie beim
  // handschriftlichen "sin"). \left/\right/\big(g)(l/r) sind reine
  // Größenmodifikatoren (kein eigenes Zeichen) — nur das folgende
  // Klammerzeichen selbst zählt. \, \; \! \: sind unsichtbare Abstände
  // (0 Zeichen). Andere Befehle mit nicht-alphabetischem Namen (\|, \{,
  // \}, \%, ...) stehen für genau EIN sichtbares Symbol.
  const MAX_ANSWER_LEN = 60;
  const WORD_MACRO_LEN = { sin:3, cos:3, tan:3, arcsin:6, arccos:6, arctan:6, exp:3, ln:2, log:3, lim:3 };
  const ZERO_WIDTH_DELIM_RE = /\\(?:left|right|bigl|bigr|Bigl|Bigr|biggl|biggr|Biggl|Biggr|big|Big|bigg|Bigg)\b/g;
  const ZERO_WIDTH_SPACE_RE = /\\[,;!:]/g;
  function meaningfulLength(latex) {
    return String(latex || "")
      .replace(/\\placeholder\{\}/g, "")
      .replace(ZERO_WIDTH_DELIM_RE, "")
      .replace(ZERO_WIDTH_SPACE_RE, "")
      .replace(/\\([a-zA-Z]+)/g, (m, name) => "X".repeat(WORD_MACRO_LEN[name] || 1))
      .replace(/\\[^a-zA-Z]/g, "X")
      .replace(/[{}]/g, "")
      .length;
  }
  function flashLimit() {
    try {
      mf.classList.add("limit-hit");
      setTimeout(() => mf.classList.remove("limit-hit"), 200);
    } catch (_) {}
  }
  // Czy WSTAWIANIE (nie zastępowanie zaznaczenia — to może skracać) jest
  // już zablokowane limitem? Współdzielone przez fizyczną klawiaturę
  // (beforeinput) i przyciski palety (handlePbtn) — dawniej sprawdzane
  // TYLKO dla fizycznej klawiatury, więc przyciski palety mogły wstawiać
  // bez ograniczeń (mf.executeCommand("insert", ...) nie wywołuje
  // natywnego zdarzenia "beforeinput").
  function isInsertBlockedByLimit() {
    if (mf.selectionIsCollapsed === false) return false;
    const cur = (mf.getValue && (mf.getValue("latex-unstyled") || mf.getValue("latex"))) || "";
    return meaningfulLength(cur) >= MAX_ANSWER_LEN;
  }

  mf.addEventListener("beforeinput", (e) => {
    try {
      const t = e.inputType || "";
      if (t.startsWith("delete") || t === "historyUndo" || t === "historyRedo") return;
      if (t !== "insertText") return;
      if (isInsertBlockedByLimit()) { e.preventDefault(); flashLimit(); }
    } catch (_) {}
  });

  const update = () => {

    // 1) latex — zawsze
    const raw = (mf && mf.getValue) ? (mf.getValue("latex-unstyled") || mf.getValue("latex") || mf.getValue("latex-expanded") || "") : "";
  
    const latex0 = cleanupLatex(raw);

    if (outLatex) outLatex.value = latex0;

    try {
      const cc = document.getElementById("charCount");
      if (cc) cc.textContent = "(" + meaningfulLength(latex0) + "/" + MAX_ANSWER_LEN + ")";
    } catch (_) {}

    try {
      const lc = document.getElementById("latexCode");
      if (lc) lc.textContent = latex0;
    } catch (_) {}

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


  // MathLive scala (koalescuje) kolejne wywołania "insert" o tym samym
  // wewnętrznym op-name w JEDEN krok cofania, tak jak zwykłe pisanie na
  // klawiaturze. Dla naszych przycisków-palety chcemy odwrotnie: każde
  // kliknięcie to osobna, jednoznaczna akcja użytkownika, więc każde ma
  // być osobnym krokiem "cofnij". Przerywamy scalanie tuż PRZED każdym
  // insertem, żeby ten insert nie doklejał się do poprzedniego.
  function breakUndoCoalescing() {
    try { mf._mathfield && mf._mathfield.stopCoalescingUndo(); } catch (_) {}
  }

  // CAPS-Taste, 3 Zustände — wie eine Telefon-Tastatur:
  //   off   -> (klik) -> shift  (einmalig: gilt nur für den NÄCHSTEN
  //                               eingefügten Buchstaben, danach automatisch
  //                               zurück zu "off")
  //   shift -> (klik, ohne zwischendurch einen Buchstaben einzufügen)
  //                               -> lock (bleibt aktiv, bis erneut geklickt)
  //   lock  -> (klik) -> off
  // Solange shift/lock aktiv ist, liefert die Kleinbuchstaben-Reihe
  // Großbuchstaben (Text + data-ins werden umgeschrieben) und die feste
  // Großbuchstaben-Reihe ist gesperrt.
  let capsState = "off";
  function setCapsState(next) { capsState = next; applyCapsState(); }
  function applyCapsState() {
    const active = capsState !== "off";
    document.querySelectorAll(".btnrow.letterrow .pbtn.lower").forEach((b) => {
      const base = b.getAttribute("data-base") || b.getAttribute("data-ins");
      const letter = active ? base.toUpperCase() : base;
      b.setAttribute("data-ins", letter);
      const i = b.querySelector("i"); if (i) i.textContent = letter;
    });
    document.querySelectorAll(".btnrow.letterrow .pbtn.const").forEach((b) => {
      b.disabled = active;
    });
    const capsBtn = document.querySelector(".capsBtn");
    if (capsBtn) {
      capsBtn.classList.remove("caps-off", "caps-shift", "caps-lock");
      capsBtn.classList.add("caps-" + capsState);
      capsBtn.setAttribute("aria-pressed", active ? "true" : "false");
    }
  }

  const handlePbtn = (e) => {
      const btn = e.target.closest(".pbtn"); if (!btn) return; try { mf.focus(); } catch(_) {}
      const cmd = btn.getAttribute("data-cmd") || "";  const ins = btn.getAttribute("data-ins") || ""; try { mf.focus(); } catch(_) {}

      // od tego miejsca to są nasze przyciski-palety:
      e.preventDefault();
      e.stopPropagation();

      if (cmd === "capsCycle" ) {
        if (capsState === "off") setCapsState("shift");
        else if (capsState === "shift") setCapsState("lock");
        else setCapsState("off");
        return;
      }
      if (cmd === "bs"        ) { try { mf.executeCommand("deleteBackward"); update(); } catch (_) {} return; }
      if (cmd === "del"       ) { try { mf.executeCommand("deleteForward");  update(); } catch (_) {} return; }
      if (cmd === "undo"      ) { try { mf.executeCommand("undo");           update(); } catch (_) {} return; }
      if (cmd === "redo"      ) { try { mf.executeCommand("redo");           update(); } catch (_) {} return; }
      if (cmd === "clear"     ) { try {  if (mf.selectionIsCollapsed === false) { breakUndoCoalescing(); mf.executeCommand("insert", ""); update(); } } catch (_) {}  return; }
      if (cmd === "selectAll" ) { try { mf.executeCommand("selectAll"); update(); } catch (_) {} return; }
      if (cmd === "move_L"    ) { try { mf.executeCommand("moveToPreviousChar"); update(); } catch(_) {} return; }
      if (cmd === "move_R"    ) { try { mf.executeCommand("moveToNextChar");     update(); } catch(_) {} return; }

      if (cmd === "capsel"    ) {
        try {
          if (mf.selectionIsCollapsed !== false) return;
          const sel = mf.selection;
          const s = (mf.getValue ? (mf.getValue(sel, "latex") || "") : "");
          // Zamień wielkość każdej łacińskiej litery w całym zaznaczeniu,
          // ale nie te wewnątrz komend LaTeX (\sin, \log, \alpha, ...) —
          // całą komendę (backslash + jej litery) traktujemy jako jeden
          // nietykalny token, żeby np. \sin nie zamieniło się w \SIN.
          const swapped = s.replace(/\\[a-zA-Z]+|[a-zA-Z]/g, (m) => {
            if (m.length > 1) return m; // to komenda LaTeX — bez zmian
            return (m >= "a" && m <= "z") ? m.toUpperCase() : m.toLowerCase();
          });
          if (swapped === s) return;
          breakUndoCoalescing();
          mf.executeCommand("insert", swapped);
          // Zamiana wielkości nie zmienia liczby atomów (te same znaki/te
          // same komendy, tylko inna wielkość) — ten sam zakres pozycji
          // można więc bezpiecznie zaznaczyć z powrotem, żeby zaznaczenie
          // nie znikało po kliknięciu.
          try { mf.selection = sel; } catch (_) {}
          update();
        } catch (_) {}
        return;
      } // cmd="capsel"

      if (cmd === "romgr") { try { breakUndoCoalescing(); cmd_romgr(mf); } catch (err) { console.error("romgr failed:", err); }  update();  return; }

      if (cmd === "copy") {
        try {
          if (mf.selectionIsCollapsed !== false) { localClipLatex = mf.getValue("latex") || ""; return; }
          const sel = mf.selection;  localClipLatex = (mf.getValue(sel, "latex") || ""); } catch (err) { console.error("copy failed:", err); }
        return;
      } // cmd === "copy"

      if (cmd === "paste") {
        try {
              if (!localClipLatex) return;
              if (isInsertBlockedByLimit()) { flashLimit(); return; }
              breakUndoCoalescing();
              mf.executeCommand("insert", localClipLatex); mf.focus(); update();
            } catch (err) { console.error("paste failed:", err); }
        return;
      } //cmd = "paste"

      function tryCmd(mf, name) { try { mf.executeCommand(name); return true; } catch(e) { return false; } }

      // extendToPreviousWord/extendToNextWord zaznaczały całe "słowo"
      // (kilka znaków naraz) zamiast jednego elementu — zamieniono na
      // odpowiedniki o granulacji pojedynczego znaku.
      if (cmd === "selL") {  try { mf.executeCommand("extendSelectionBackward"); } catch (_) {}  update(); return; }
      if (cmd === "selR") {  try { mf.executeCommand("extendSelectionForward");  } catch (_) {}  update(); return; }
      if (ins) {
        if (isInsertBlockedByLimit()) { flashLimit(); try { mf.focus(); } catch(_) {} return; }
        // wrapBtn (Klammern um die Auswahl): nach dem Einfügen die
        // Auswahl auf den kompletten neuen Ausdruck INKL. der Klammern
        // ausdehnen, statt sie (wie sonst üblich) kollabiert zu lassen.
        const wrapSel = btn.classList.contains("wrapBtn") && mf.selectionIsCollapsed === false;
        const wrapStart = wrapSel ? mf.selection.ranges[0][0] : null;
        try { breakUndoCoalescing(); mf.executeCommand("insert", ins); update(); } catch (_) {}
        if (wrapSel) {
          try { const wrapEnd = mf.selection.ranges[0][1]; mf.selection = { ranges: [[wrapStart, wrapEnd]] }; } catch (_) {}
        }
        // "shift" jest jednorazowy: po wstawieniu jednej litery z rzędu
        // małych liter samo wraca do "off". "lock" tak nie działa.
        if (capsState === "shift" && btn.classList.contains("lower")) setCapsState("off");
      }
      try { mf.focus(); } catch(_) {} };

      // Uwaga: NIE wolno wołać preventDefault() na pointerdown/touchstart tutaj —
      // na iOS/WebKit dla elementów z -webkit-appearance:none to potrafi całkowicie
      // zablokować późniejsze zdarzenie "click". handlePbtn i tak przywraca focus
      // po kliknięciu, więc pole traci focus tylko na moment.

      document.addEventListener("click", handlePbtn, true);

      const form = mf.closest("form"); if (form) form.addEventListener ( "submit" , () => { try { update(); } catch (e) {} } );

      window.addEventListener ( "load" ,  () => { if (window.MathfieldElement && window.ComputeEngine) { MathfieldElement.computeEngine = new ComputeEngine.ComputeEngine(); } } );

      update();

      const focusAtEnd = () => { try { mf.focus(); mf.executeCommand("moveToMathfieldEnd"); } catch (_) {} };
      focusAtEnd();
      setTimeout(focusAtEnd, 0);
      window.addEventListener("load", () => setTimeout(focusAtEnd, 50));

  }
); // Ende von Listener: DOMContentLoaded
