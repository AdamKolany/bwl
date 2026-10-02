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

        // MathLive-Kontextmenü ("Insert Matrix" usw., per Rechtsklick oder
        // langem Drücken) abschalten. Das HTML-Attribut menu="false" gibt es
        // in MathLive nicht — es wirkt nur menuItems = []. Das Setter wirft,
        // solange das Feld nicht "mounted" ist, daher auch beim "mount".
        // Zusätzlich das contextmenu-Ereignis schon in der Capture-Phase
        // verwerfen (MathLive ignoriert defaultPrevented-Ereignisse) und das
        // Matrix-/Umgebungs-Popover abschalten.
        const killMenu = () => {
          try { mf.menuItems = []; } catch (_) {}
          try { mf.environmentPopoverPolicy = "off"; } catch (_) {}
        };
        killMenu(); mf.addEventListener("mount", killMenu);
        window.addEventListener("contextmenu", (e) => {
          const t = e.target;
          if (t && t.closest && t.closest("math-field, #palette, .answerRow")) e.preventDefault();
        }, { capture: true });
      
        if (!MathfieldElement.computeEngine && window.ComputeEngine) { MathfieldElement.computeEngine = new ComputeEngine.ComputeEngine(); }

        const ce = MathfieldElement.computeEngine; if (!ce) { console.error("ComputeEngine missing"); return; }

        let ltxval= outLatex.value;  ltx.textContent = prettyPrimes(ltxval);
        //let mjsval= outMJ.value;     mjs.textContent = 'wait';// mjsval.replace(/"/g,'').replace(/,/g,' , ').replace(/(\[\|\])/g," \$1 ");
        
        
        // AUS (2026-10-01): auf dem iPad löst JEDER Tastendruck auf der Palette
        // ein blur aus; das setValue() hier baute das Feld jedes Mal neu auf und
        // erzeugte z. B. ein nicht löschbares "p^2^{}". Leere ^{}/_{} werden
        // ohnehin in update() per cleanupLatex() aus dem abgeschickten Wert entfernt.
        // mf.addEventListener("blur", cleanMathfieldInPlace);

  
        if (!window.__ceDeclaredFG) {
            window.__ceDeclaredFG = true;  
            const decl = { f: "(number)->number", g: "(number)->number", h: "(number)->number", /* np. p: "(number, number)->number" */ };
            for (const [name, sig] of Object.entries(decl)) { try { ce.declare(name, sig); } catch (_) {}  }
        }

        ( function patchMathLiveHighlight() {
            if (!mf || !mf.shadowRoot) return;

            // Früher opacity:0.05 auf dem ganzen Element — dadurch wurde der
            // INHALT (Platzhalter-Kästchen im Exponenten, Bruch, ...) fast
            // unsichtbar (iPad, 2026-10-01). Jetzt nur ein blasser Hintergrund;
            // Platzhalter (▢) voll deckend und dunkler (Standard: opacity 0.4).
            const css = `
            .ML__contains-highlight{
              background: rgba(255,255,0,0.12) !important;
            }
            .ML__placeholder,
            .ML__selected .ML__placeholder,
            .ML__focused .ML__selected .ML__placeholder{
              opacity: 1 !important;
              color: #1f4f8f !important;
              -webkit-text-stroke: 0.06em #1f4f8f;   /* dünne Linie von ▢ verstärken (iPad, Bruch/Exponent = kleine Schrift) */
            }`;

            // nie dubluj
            if (mf.shadowRoot.getElementById("ml-highlight-fix")) return;

            const st = document.createElement("style");
            st.id = "ml-highlight-fix";
            st.textContent = css;
            mf.shadowRoot.appendChild(st);
          } 
        ) ();

  // Das Palette-"e" (Eulersche Zahl) wird fett als \mathbf{e} eingefuegt,
  // in den hinterlegten Antworten steht aber ein normales e. Fuer die
  // LaTeX-Ausgabe und die Auswertung daher \mathbf{e} / \boldsymbol{e} /
  // \bm{e} wieder zu e machen (nur exakt das e, nicht \mathbf{Dm} o.ae.).
  function unboldEulerE(s) {
    return (s || "")
      // \cdot\mathbf{e} -> \cdot e (nicht \cdote): Leerzeichen nach einem Befehl erhalten
      .replace(/(\\[A-Za-z]+)\s*(?=\\(?:mathbf|boldsymbol|bm)(?![A-Za-z]))/g, "$1 ")
      .replace(/\\(?:mathbf|boldsymbol|bm)\s*\{\s*e\s*\}/g, "e")
      .replace(/\\(?:mathbf|boldsymbol|bm)\s+e(?![A-Za-z])/g, "e");
  }

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

  // --- Numerischer Gleichheitstest (Monte Carlo) --------------------------
  // Der rein symbolische Vergleich (diff.isEqual(0)) liefert nur dann ein
  // sicheres true, wenn die Antwort AEHNLICH geschrieben ist wie die
  // Musterloesung. Algebraisch gleiche, aber anders notierte Antworten
  // (z.B. sin(6x-13)/6 statt (1/6)sin(6x-13), Summanden umgestellt) bleiben
  // unentschieden und wurden bisher als falsch gewertet. Fallback: beide
  // Seiten an mehreren zufaelligen Punkten auswerten und vergleichen.
  const _MC_KNOWN = new Set(["Pi","ExponentialE","ImaginaryUnit","GoldenRatio",
    "EulerGamma","CatalanConstant","MachineEpsilon","True","False","Nothing",
    "Infinity","ComplexInfinity","NaN","Half"]);

  function _mcSymbols(mj, acc) {
    if (typeof mj === "string") {
      if (!_MC_KNOWN.has(mj) && /^[A-Za-z][A-Za-z0-9_]*$/.test(mj)) acc.add(mj);
      return;
    }
    if (Array.isArray(mj)) { for (let i = 1; i < mj.length; i++) _mcSymbols(mj[i], acc); return; }
    if (mj && typeof mj === "object") {
      if (typeof mj.sym === "string") { _mcSymbols(mj.sym, acc); return; }
      if (Array.isArray(mj.fn)) { for (let i = 1; i < mj.fn.length; i++) _mcSymbols(mj.fn[i], acc); return; }
    }
  }

  function _mcReIm(x) {
    if (x == null) return [NaN, 0];
    if (typeof x.re === "number" || typeof x.im === "number")
      return [typeof x.re === "number" ? x.re : NaN, typeof x.im === "number" ? x.im : 0];
    let v = x;
    try { if (typeof x.value === "number") return [x.value, 0]; } catch (_) {}
    try { if (typeof x.valueOf === "function") v = x.valueOf(); } catch (_) {}
    if (typeof v === "number") return [v, 0];
    if (v && typeof v.re === "number") return [v.re, v.im || 0];
    const n = Number(v);
    return [Number.isNaN(n) ? NaN : n, 0];
  }

  // true  = an allen gueltigen Stichproben gleich
  // false = an mindestens einer Stichprobe verschieden
  // undefined = zu wenige auswertbare Stichproben -> keine Aussage
  function monteCarloEqual(CE, a, b, N, TOL) {
    N = N || 24; TOL = TOL || 1e-6;
    let syms;
    try {
      const set = new Set();
      _mcSymbols(a.json, set); _mcSymbols(b.json, set);
      syms = [...set];
    } catch (_) { return undefined; }

    let good = 0, bad = 0, used = 0;
    for (let t = 0; t < N; t++) {
      const sub = {};
      // moderater positiver Bereich -> haelt \sqrt, \ln, Division usw. definiert
      for (const v of syms) sub[v] = CE.box(0.35 + 4.65 * Math.random());
      let va, vb;
      try {
        va = _mcReIm((syms.length ? a.subs(sub) : a).N());
        vb = _mcReIm((syms.length ? b.subs(sub) : b).N());
      } catch (_) { continue; }
      if (![va[0], va[1], vb[0], vb[1]].every(Number.isFinite)) continue;
      used++;
      const d = Math.hypot(va[0] - vb[0], va[1] - vb[1]);
      const scale = Math.max(1, Math.hypot(va[0], va[1]), Math.hypot(vb[0], vb[1]));
      if (d <= TOL * scale) good++; else bad++;
      if (!syms.length) break; // konstanter Ausdruck: eine Auswertung genuegt
    }
    if (used < (syms.length ? 6 : 1)) return undefined;
    return bad === 0 && good > 0;
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

  const update = (final) => {

    // 1) latex — zawsze
    const raw = (mf && mf.getValue) ? (mf.getValue("latex-unstyled") || mf.getValue("latex") || mf.getValue("latex-expanded") || "") : "";
  
    const latex0 = unboldEulerE(cleanupLatex(raw));

    if (outLatex) outLatex.value = latex0;

    try {
      const cc = document.getElementById("charCount");
      if (cc) cc.textContent = "(" + meaningfulLength(latex0) + "/" + MAX_ANSWER_LEN + ")";
    } catch (_) {}

    try {
      const lc = document.getElementById("latexCode");
      if (lc) lc.textContent = latex0;
    } catch (_) {}

    answer = document.getElementById("answer"); if (answer) latex1 = unboldEulerE(answer.getAttribute("data-answer"));
    
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

      // Bewertung (CE-Vergleich + Monte Carlo) ist teuer und wird NICHT
      // bei jedem Tastendruck gebraucht — nur beim Absenden (final).
      if (final && mjs) {

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

        let eq = (diff.isEqual(0) === true);
        if (!eq && monteCarloEqual(CE, json0c, json1c) === true) eq = true;
        document.getElementById('richtig').value = eq ? 'J' : 'N';
        const s1=document.getElementById('score');
        s1.dataset.score = eq ? 1 : 0;
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

  mf.addEventListener("input", () => update());


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

  // "heraus": eine Ebene hinaus (aus dem innersten Exponenten, Bruchteil,
  // Wurzel, Klammer, ...). Unsichtbare Gruppen {…} (z. B. der Nenner aus
  // \frac{#0}{{#?}}) zählen nicht als Ebene — sonst passiert sichtbar nichts.
  function exitContext(mf) {
    const model = mf._mathfield && mf._mathfield.model;
    for (let i = 0; i < 20; i++) {
      let parent = null;
      try { parent = model ? model.at(model.position).parent : null; } catch (_) {}
      if (!mf.executeCommand("moveAfterParent")) return;
      if (!parent || parent.type !== "group") return;
    }
  }

  // Auswahl um ein GANZES Element erweitern (Bruch, Potenz, Wurzel, ...).
  // MathLives extendSelectionForward/Backward geht nur eine Position in der
  // flachen Atomfolge weiter, also schrittweise IN Zähler, Exponent, Nenner
  // hinein — die Zwischenauswahlen sind halbe Konstrukte, die Markierung
  // blinkt bei jedem Druck auf und verschwindet wieder (iPad, 2026-10-02).
  // Hier: so lange weitergehen, bis das Ende wieder auf der Ebene des Ankers
  // (oder darüber) liegt.
  function extendSelectionWhole(mf, dir) {
    const model = mf._mathfield && mf._mathfield.model;
    const fallback = () => mf.executeCommand(dir > 0 ? "extendSelectionForward" : "extendSelectionBackward");
    if (!model || typeof model.at !== "function") return fallback();
    const depth = (a) => { let d = 0; for (; a && a.parent; a = a.parent) d++; return d; };
    const anchor = model.anchor, last = model.lastOffset;
    const d0 = depth(model.at(anchor));
    let pos = model.position;
    do { pos += dir; } while (pos > 0 && pos < last && depth(model.at(pos)) > d0);
    pos = Math.max(0, Math.min(last, pos));
    mf.selection = pos >= anchor ? { ranges: [[anchor, pos]], direction: "forward" }
                                 : { ranges: [[pos, anchor]], direction: "backward" };
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
      if (cmd === "exitCtx"   ) { try { exitContext(mf); update(); } catch(_) {} return; }
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
      if (cmd === "selL") {  try { extendSelectionWhole(mf, -1); } catch (_) {}  update(); return; }
      if (cmd === "selR") {  try { extendSelectionWhole(mf, +1); } catch (_) {}  update(); return; }
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

      const form = mf.closest("form"); if (form) form.addEventListener ( "submit" , () => { try { update(true); } catch (e) {} } );

      window.addEventListener ( "load" ,  () => { if (window.MathfieldElement && window.ComputeEngine) { MathfieldElement.computeEngine = new ComputeEngine.ComputeEngine(); } } );

      update();

      const focusAtEnd = () => { try { mf.focus(); mf.executeCommand("moveToMathfieldEnd"); } catch (_) {} };
      focusAtEnd();
      setTimeout(focusAtEnd, 0);
      window.addEventListener("load", () => setTimeout(focusAtEnd, 50));

  }
); // Ende von Listener: DOMContentLoaded
