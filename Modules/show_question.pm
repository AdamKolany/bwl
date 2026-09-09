package show_question;

use CGI qw(:standard escapeHTML);
use utf8;
use strict;

require './Modules/Common.pm';
require './Modules/DB.pm';

# ============================================================
# Frage
# ============================================================
sub run {
  my $nr = $Common::cgi->param('nr') // 1;
  $nr =~ s/\D//g; $nr ||= 1;

  Common::send_redirect(qs => "action=menu" . ($Common::cgi->param('debug') ? "&debug=1" : "")) unless $Common::sid;

  my ($qid, $qtxt, $status) = $DB::dbh->selectrow_array(
      q{ SELECT q.frage_id, p.frage, p.status FROM session_questions q JOIN fragen p ON p.frage_id = q.frage_id WHERE q.sessionid = ? AND q.nr = ?  },
      undef, $Common::sid, $nr);

  my $qids = $DB::dbh->selectall_arrayref(q{ select frage_id from session_questions where sessionid = ?}, undef,$Common::sid);
  my @qlist=(); for my $i (@$qids){ (my $j)=@$i; push @qlist, $j ; }
        
  my $qnum = @$qids;
      
  Common::send_redirect(qs => "action=result" . ($Common::cgi->param('debug') ? "&debug=1" : "")) unless defined $qid;

  my $answer     = $DB::dbh->selectall_arrayref(q{ SELECT antwort_id, antwort, richtig,antwort_latex FROM antworte WHERE frage_id = ? ORDER BY antwort_id  }, undef, $qid);
  my ($total) = $DB::dbh->selectrow_array(q{SELECT COUNT(*) FROM geschichte WHERE sessionid = ?}, undef, $Common::sid);
  my ($good)  = $DB::dbh->selectrow_array(q{SELECT COUNT(*) FROM geschichte WHERE sessionid = ? AND richtig = 'J'}, undef, $Common::sid);
  $total ||= 0; $good ||= 0;

  HTML::page_header("Frage $nr"); 
  
  # print "<div id='appscale'> <div id='appcontent'>";

  print qq{ <style> body {zoom: 1;} </style>  };

  Common::debug_block();

  my ( $qqlist, $qlist)=("",join(',&nbsp;',@qlist) );
  my @qqlist = ( @qlist[0..($nr-2)] , sprintf("<span style='color: red; font-size: 1.10em;'>%d</span>",$qlist[$nr-1]), @qlist[($nr)..$#qlist] );
  $qqlist=join(',&nbsp;',@qqlist);
  my ($kapitel,$thema) =
      $DB::dbh->selectrow_array(q{select k.kapitel,t.thema from session_quiz s, themen t, kapitel k where k.kap_kürzel = s.kapitel and t.th_kürzel=s.thema and sessionid = ?}, undef, $Common::sid);

  
  print("<p class='line' style='color: gray; font-size:1.2em; margin-top: -5px;'>[SID: $Common::sid] <span class='right' style='font-size:0.8em; color: indianred;'>[$qqlist]</span></p>");

  my $dbg = $Common::cgi->param('debug') ? "&debug=1" : "";

  # my $score = $Common::cgi->param('score') // 0;


  my $kind = Common::status_kind($status); 

  my $ua = $ENV{'HTTP_USER_AGENT'} // '';
  print "<p class='line' style='font-size: 1.0em; color: gray;'>$ua</p>";
  print "<p class='line'>",   
      "<span style='font-size: 1.2em; margin-top: 0px;' >[ $kapitel / $thema ]</span>",
      "<a href='?action=menu$dbg' class='small' style='text-decoration: none; margin-left: 20px; '>Menu</a>",
      "<span class='right' style='color: gray;'> [<span id='xysize'></span>]</span>",
      "</p>" ;

  print qq{ <div class="sep"></div> };

  print "<h4>",
    "<p class='line' style=''>Frage $nr/$qnum  &nbsp;&nbsp;&nbsp;($qid) ",
      "<span style='color: lightblue;' class='right'>", sprintf("[Pkt: % 2d/% 2d]", $good, $total ),"</span>",
    "</p>", 
    "</h4>";

  print p({class=>'q'}, Common::htxt($qtxt));  
  
  print qq{<div class="sep"></div>};
  
  my $multi = Common::is_multi_status($status); # print p({class=>'small'}, $multi ? "Mehrfachwahl" : "Einfachswahl");

  print qq{<div class="sep"></div>};
  
  print start_form(-method=>'POST', -action=>$Common::SELF);
  print hidden(-name=>'nr', -value=>$nr);
  print hidden(-name=>'qid', -value=>$qid);
  print hidden(-name=>'debug', -value=>1) if $Common::cgi->param('debug');

  my $kind = Common::status_kind($status);
  if ($kind eq 'single' || $kind eq 'multi') {
    # immer Checkboxen; für 'single' wird clientseitig "radio-Verhalten" erzwungen
      print qq{<fieldset><legend>Antworten</legend>};
      my $single = ($kind eq 'single') ? 1 : 0;
      my $type = $multi ? "checkbox" : "radio";

    for my $r (@$answer) {
      my ($aid, $atxt,$aval) = @$r;
      next unless defined $aid && $aid =~ /^\d+$/;
      my $col = ($aval eq "J") ? "blue" : "black";
      my $ds  = $single ? ' data-single="1"' : '';
      my $chk=($aval eq "J")?"checked":"";    
      print 
      qq{<label class="ans" style="color:$col;"><input type="$type" name="aid" value="$aid" $chk> } 
      . Common::htxt($atxt) . 
      qq{</label>\n};
    }
    print qq{</fieldset>};
    # Radio-Verhalten für 'single'
    if ($single) {
      print qq{
      <script>
       document.addEventListener('change', (e) => {
        const el = e.target; 
        if (!el || el.tagName !== 'INPUT') return; 
        if (el.type !== 'checkbox') return; 
        if (!el.matches('input[name="aid"][data-single="1"]')) return; 
        if (!el.checked) return;
        document.querySelectorAll('input[name="aid"][data-single="1"]').forEach(cb => { if (cb !== el) cb.checked = false; });
       });
      </script>
      };
     }
    }  elsif ($kind eq 'open') {
     print qq{<fieldset><legend>Antwort (Text)</legend>};
     my $v = $Common::cgi->param('user_text') // '';
     $v = '…' if $v =~ /^\s*$/;
     print qq{<textarea class="open" name="user_text" rows="1">} . $Common::render->($v) . qq{</textarea>};
     print qq{</fieldset>};
  }  elsif ($kind eq 'formel') { # Hier  Mathe !!! 
      my @answer=();
      for my $r (@$answer) {
        my ($aid, $atxt,$aval,$ltx) = @$r; # HERE
        next unless defined $aid && $aid =~ /^\d+$/;
        if ($aval eq "J") { push @answer, $ltx; }
      }

      my ($hint)  = $DB::dbh->selectrow_array(q{ SELECT hint FROM antworte WHERE frage_id = ? ORDER BY antwort_id  }, undef, $qid);

      my $skipp=qq{<span class="skip"></span>};
      my $break=qq{<span class="br"></span>};
 
      sub toRight  { print qq{<span style="display: block; margin-left: auto; text-align: right;"></span>}; };
      sub toLeft   { print qq{<span style="display: block; margin-right: auto; text-align: left;"></span>}; };
      sub centered { print qq{<span style="display: block; margin-left: auto; margin-right: auto; text-align: center;"></span>}; };
      sub break    { print qq{<span class="br"></span>}; }
      sub skipp    { (my $c) = @_;  for (my $i = 0; $i < $c/2; $i++) { print qq{<span class="skip"></span>}; } };
      
      my $richtig = '<span id="score" data-score="0" style="margin-left:auto; color: red; font-weight:bold;"></span>';
      my $charCount = '<span id="charCount" style="font-weight:normal; font-size:0.75em; color:gray;"></span>';
      my $latexCode = '<span id="latexCode" style="font-weight:normal; font-size:0.75em; color:#bbb; margin-left:1.5em; padding:0.1em 0.5em; border:1px solid #ddd; border-radius:4px;"></span>';

      my $svgMoveLine = qq{width="1.05em" height="1.05em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="k-icon"};
      my $svg_moveL   = qq{<svg $svgMoveLine><path d="M20 12H4"/><path d="M10 6L4 12L10 18"/></svg>};
      my $svg_moveR   = qq{<svg $svgMoveLine><path d="M4 12H20"/><path d="M14 6L20 12L14 18"/></svg>};

      print qq{<fieldset><legend>Antwort $charCount$latexCode&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$richtig</legend>};
      
      print qq{};
      
my $latex0 = $Common::cgi->param('user_latex') // $$answer[3]; $latex0 = join ', ', @answer if $latex0 =~ /^\s*$/;

print qq{<div class="answerRow">};
# print qq{<div class="mf-scroll">};
print qq{<math-field id="mf" class="ml" virtual-keyboard-mode="off" menu="false">}
    . Common::htxt($hint) 
    . qq{</math-field>};
print qq{<div id="answer" data-answer="$latex0"></div>};

print qq{
  <div class="weiterCol">
    <div class="cpRow">
      <button type="button" class="pbtn" data-cmd="copy">→📋</button>
      <button type="button" class="pbtn" data-cmd="paste">📋→</button>
    </div>
    <button class="btn" type="submit" name="action" value="save">weiter</button>
    <div class="cpRow">
      <button type="button" class="pbtn moveBtn" data-cmd="move_L">$svg_moveL</button>
      $skipp
      <button type="button" class="pbtn moveBtn" data-cmd="move_R">$svg_moveR</button>
    </div>
  </div>
};

print qq{</div>};


     print qq{<div class="palette palette2" style="margin-top:-30px;" id="palette">};

      # --- neue kompakte Tastatur (v2) ---------------------------------
      my $svgLine = qq{width="1.05em" height="1.05em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="k-icon"};
      my $svgFill = qq{width="1.05em" height="1.05em" viewBox="0 0 24 24" fill="currentColor" stroke="none" class="k-icon"};
      my $svgBoxA = qq{width="0.68em" height="0.68em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" class="k-icon k-box"};
      my $svgAccA = qq{width="0.68em" height="0.85em" viewBox="0 0 24 30" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" class="k-icon k-box"};

      # Platzhalter-Kästchen (□) als SVG statt Unicode-Zeichen, damit es auf
      # allen Plattformen/Fonts gleich aussieht (dieselbe Ursache wie die
      # ursprünglichen ⌫⌦⊠-Zeichen). $svg_ovl/$svg_hat verwenden dieselbe
      # Kästchengröße (18x18) wie $svg_box, nur in einer höheren Leinwand,
      # damit oben Platz für den Akzent bleibt — beide mit demselben Abstand
      # (Grundlinie bei y=5) zwischen Akzent und Kästchen.
      my $svg_box = qq{<svg $svgBoxA><rect x="3" y="3" width="18" height="18" rx="3"/></svg>};

      # "Basis"-Kästchen der Potenz-/Index-Icons: gleiche Breite wie $svg_box,
      # aber 1.5x so hoch (Rechteck statt Quadrat) — nur für die
      # <span class="base">, nicht für Exponent/Index/Bruch-Kästchen.
      my $svgBaseBoxA = qq{width="0.68em" height="1.02em" viewBox="0 0 24 36" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" class="k-icon k-box"};
      my $svg_baseBox = qq{<svg $svgBaseBoxA><rect x="3" y="4.5" width="18" height="27" rx="3"/></svg>};
      my $svg_ovl = qq{<svg $svgAccA><rect x="3" y="11" width="18" height="18" rx="3"/><line x1="3" y1="5" x2="21" y2="5"/></svg>};
      my $svg_hat = qq{<svg $svgAccA><rect x="3" y="11" width="18" height="18" rx="3"/><path d="M6 5L12 1L18 5"/></svg>};

      # Echtes Bruch-Icon: zwei liegende (breite, flache) Kästchen als
      # Zähler/Nenner, getrennt durch einen waagerechten Bruchstrich —
      # statt des alten "□/□"-Schrägstrich-Layouts.
      my $svgFracA = qq{width="1.0em" height="1.0em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" class="k-icon k-box"};
      my $svg_fracIcon = qq{<svg $svgFracA><rect x="4" y="1" width="16" height="7" rx="2"/><line x1="2" y1="12" x2="22" y2="12"/><rect x="4" y="16" width="16" height="7" rx="2"/></svg>};

      my $svg_bs        = qq{<svg $svgLine><path d="M8 4H20A1 1 0 0 1 21 5V19A1 1 0 0 1 20 20H8L3 12L8 4Z"/><path d="M11 9L17 15"/><path d="M17 9L11 15"/></svg>};
      my $svg_del       = qq{<svg $svgLine><path d="M4 4H16L21 12L16 20H4A1 1 0 0 1 3 19V5A1 1 0 0 1 4 4Z"/><path d="M7 9L13 15"/><path d="M13 9L7 15"/></svg>};
      my $svg_clear     = qq{<svg $svgLine><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8L16 16"/><path d="M16 8L8 16"/></svg>};
      my $svg_selL      = qq{<svg $svgFill><path d="M16 4L6 12L16 20Z"/></svg>};
      my $svg_selR      = qq{<svg $svgFill><path d="M8 4L18 12L8 20Z"/></svg>};
      my $svg_selectAll = qq{<svg $svgFill><path d="M12 2L14.59 8.36L21.51 8.82L16.06 13.14L17.93 19.86L12 16.1L6.07 19.86L7.94 13.14L2.49 8.82L9.41 8.36Z"/></svg>};
      my $svg_undo      = qq{<svg $svgLine><path d="M7 7H3V3"/><path d="M3 7C4.5 4 7.8 2 11.5 2C16.7 2 21 6.3 21 11.5C21 16.7 16.7 21 11.5 21C7.6 21 4.2 18.5 3 15"/></svg>};
      my $svg_redo      = qq{<svg $svgLine><path d="M17 7H21V3"/><path d="M21 7C19.5 4 16.2 2 12.5 2C7.3 2 3 6.3 3 11.5C3 16.7 7.3 21 12.5 21C16.4 21 19.8 18.5 21 15"/></svg>};

      # CAPS-Taste, 3 Zustände (OFF/SHIFT/LOCK) — dieselbe Pfeil-Silhouette
      # wie bei den üblichen Telefon-Tastaturen: OFF = nur Umriss, SHIFT =
      # gefüllt, LOCK = gefüllt + Unterstrich.
      my $capsArrowPath = "M12 3L4 12H9V16H15V12H20Z";
      my $svg_capsOff   = qq{<svg $svgLine><path d="$capsArrowPath"/></svg>};
      my $svg_capsShift = qq{<svg $svgFill><path d="$capsArrowPath"/></svg>};
      my $svg_capsLock  = qq{<svg $svgFill><path d="$capsArrowPath"/><rect x="4" y="19" width="16" height="2.5" rx="1"/></svg>};

      my $navicons=
        qq{<span class="navgrp">}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="bs"     title="Backspace">$svg_bs</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="del"    title="Löschen">$svg_del</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="clear" title="Auswahl löschen">$svg_clear</button>}.
        qq{</span>}.
        qq{<span class="navgrp">}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selL">$svg_selL</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selR">$svg_selR</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selectAll">$svg_selectAll</button>}.
        qq{</span>}.
        qq{<span class="navgrp">}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="undo">$svg_undo</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="redo">$svg_redo</button>}.
        qq{</span>};

      my $capsel= qq{<button type="button" class="pbtn capselBtn" data-cmd="capsel"><span class='m'>az ↔ AZ</span></button>};
      # Alle 3 Icons liegen im DOM, CSS zeigt je nach caps-off/-shift/-lock
      # Klasse auf dem Button nur eines davon — JS muss also nur die Klasse
      # umschalten, nicht das innerHTML neu zusammensetzen.
      my $capsBtn = qq{<button type="button" class="pbtn pbtn1 capsBtn caps-off" data-cmd="capsCycle" title="Caps">}.
                    qq{<span class="capsIcon capsIcon-off">$svg_capsOff</span>}.
                    qq{<span class="capsIcon capsIcon-shift">$svg_capsShift</span>}.
                    qq{<span class="capsIcon capsIcon-lock">$svg_capsLock</span>}.
                    qq{</button>};

      # Zeile 1: Umschalter + Navigations-/Editier-Icons
      print "<div class='btnrow navrow'>";
      print $capsBtn; print $capsel; print $navicons;
      print "</div>"; break();

      # Zeile 2: Kleinbuchstaben, Ziffern
      print "<div class='btnrow letterrow centeredRow'>";
      for my $l ('a'..'z') { print qq{<button type="button" class="pbtn lower" data-ins="$l" data-base="$l"><i>$l</i></button>}; }
      skipp(4);
      for my $l (0..9) { print qq{<button type="button" class="pbtn" data-ins="$l"><i>$l</i></button>}; }
      print "</div>"; break();

      # Zeile 3: Grundrechenarten, Potenzen/Wurzeln, Beträge/Normen
      print "<div class='btnrow algebraRow'>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="="><span class='mathbtn' data-tex="="></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="+"><span class='mathbtn' data-tex="+"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="-"><span class='mathbtn' data-tex="-"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="·"><span class='mathbtn' data-tex="\\cdot"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="/"><span class='mathbtn' data-tex="\\div"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\frac{#0}{{#?}}">$svg_fracIcon</button>};

      if (1) {
	  print qq{<button type="button" class="pbtn eqw" data-ins="#0^2"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup">2</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw" data-ins="#0^3"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup">3</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw" data-ins="#0^{#?}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup boxsup">$svg_box</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw eqwNF" data-ins="#0^{{#?}/{#?}}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup nicefrac"><span class="n">$svg_box</span><span class="slash">/</span><span class="d">$svg_box</span></span></span></button>};
      } else {
	  print qq{<button type="button" class="pbtn eqw" data-ins="{{}^2}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup">2</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw" data-ins="{{}^3}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup">3</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw" data-ins="{{}^{#?}}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup boxsup">$svg_box</span></span></button>};
	  print qq{<button type="button" class="pbtn eqw eqwNF" data-ins="{{}^{{#?}/{#?}}}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup nicefrac"><span class="n">$svg_box</span><span class="slash">/</span><span class="d">$svg_box</span></span></span></button>};
      }
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[2]{#0}"><span class="m">²√</span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[3]{#0}"><span class="m">³√</span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[#?]{#0}"><span class="m">ⁿ√</span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\left|#0\\right|"><span class='mathbtn tr' data-tex="\\left|\\cdot\\right|"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\big|"><span class='mathbtn tr' data-tex="\\big|"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\big\\|"><span class='mathbtn tr' data-tex="\\big\\|"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn eqw eqwSub" data-ins="#0_{#?}"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sub">$svg_box</span></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\overline{#0}">$svg_ovl</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\hat{#0}">$svg_hat</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn eqw" data-ins="\\big(#?\\,\\big|\\,\#0\\big)"><span class='mathbtn tr' data-tex="(\\cdot\\,|\\,\\cdot)"></span></button>};
      print qq{<button type="button" class="pbtn eqw" data-ins="\\left\\langle#0\\,{,}\\,#?\\right\\rangle"><span class='mathbtn tr' data-tex="\\left\\langle\\cdot\\,{,}\\,\\cdot\\right\\rangle"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\bullet"><span class='mathbtn' data-tex="\\bullet"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\circ"><span class='mathbtn' data-tex="\\circ"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\times"><span class='mathbtn' data-tex="\\times"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn eqw" data-ins="#0^\\top"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup supNear supTop">⊤</span></span></button>};
      print qq{<button type="button" class="pbtn eqw" data-ins="#0^\\ast"><span class="xmsub"><span class="base">$svg_baseBox</span><span class="sup supAst">*</span></span></button>};
      print "</span>";

      print "</div>"; break();

      # Zeile 4: Relationen, Mengenlehre, Zahlenbereiche
      print "<div class='btnrow algebraRow'>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\approx"><span class='mathbtn' data-tex="\\approx"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\ne"><span class='mathbtn' data-tex="\\neq"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\pm"><span class='mathbtn' data-tex="\\pm"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="<"><span class='mathbtn' data-tex="<"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins=">"><span class='mathbtn' data-tex=">"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\leqslant"><span class='mathbtn' data-tex="\\leqslant"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\geqslant"><span class='mathbtn' data-tex="\\geqslant"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\subseteq"><span class='mathbtn' data-tex="\\subseteq"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\subsetneq"><span class='mathbtn' data-tex="\\subsetneq"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\cup"><span class='mathbtn' data-tex="\\cup"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\cap"><span class='mathbtn' data-tex="\\cap"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\setminus"><span class='mathbtn' data-tex="\\setminus"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\in"><span class='mathbtn' data-tex="\\in"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\notin"><span class="mathbtn" data-tex="\\notin"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\varnothing"><span class='mathbtn' data-tex="\\varnothing"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\bigcup"><span class='mathbtn' data-tex="\\bigcup"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\bigcap"><span class='mathbtn' data-tex="\\bigcap"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{N}"><span class='mathbtn' data-tex="\\mathbb{N}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{Z}"><span class='mathbtn' data-tex="\\mathbb{Z}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{Q}"><span class='mathbtn' data-tex="\\mathbb{Q}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{R}"><span class='mathbtn' data-tex="\\mathbb{R}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{C}"><span class='mathbtn' data-tex="\\mathbb{C}"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\imath"><span class='mathbtn' data-tex="\\imath"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\infty"><span class='mathbtn' data-tex="\\infty"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\xrightarrow[#0\\to#?]{}"><span class='mathbtn tr' data-tex="\\xrightarrow[n\\to\\infty]{}"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn domRg" data-ins="\\mathbf{Dm}\\left(#0\\right)">Dm</button>};
      print qq{<button type="button" class="pbtn domRg" data-ins="\\mathbf{Rg}\\left(#0\\right)">Rg</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\left((#0,#0)\\mapsto#?\\right)"><span class='mathbtn' data-tex="\\mapsto"></span></button>};
      print "</span>";

      print "</div>"; break();

      # Zeile 5: Klammern/Intervalle, Logik, griechische Buchstaben
      print "<div class='btnrow algebraRow'>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn wrapBtn" data-ins="\\left(#0\\right)"><span class='mathbtn tr' data-tex="\\left(\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn wrapBtn" data-ins="\\left[#0\\right]"><span class='mathbtn tr' data-tex="\\left[\\cdot\\right]"></span></button>};
      print qq{<button type="button" class="pbtn wrapBtn" data-ins="\\left\\{#0\\right\\}"><span class='mathbtn tr' data-tex="\\left\\{\\cdot\\right\\}"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\left\\{#0:\\,#?\\right\\}"><span class='mathbtn tr' data-tex="\\left\\{\\cdot:\\,\\ldots\\right\\}"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\left(#0\\,,\\;#?\\right)"><span class='mathbtn tr' data-tex="\\left(\\cdot\\,,\\;\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left[#0\\,,\\;#?\\right]"><span class='mathbtn tr' data-tex="\\left[\\cdot\\,,\\;\\cdot\\right]"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left[#0\\,,\\;#?\\right)"><span class='mathbtn tr' data-tex="\\left[\\cdot\\,,\\;\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left(#0\\,,\\;#?\\right]"><span class='mathbtn tr' data-tex="\\left(\\cdot\\,,\\;\\cdot\\right]"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\forall"><span class='mathbtn' data-tex="\\forall"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\exists"><span class='mathbtn' data-tex="\\exists"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\neg"><span class='mathbtn' data-tex="\\neg"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\vee"><span class='mathbtn' data-tex="\\vee"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\wedge"><span class='mathbtn' data-tex="\\wedge"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\Rightarrow"><span class='mathbtn' data-tex="\\Rightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\Leftrightarrow"><span class='mathbtn' data-tex="\\Leftrightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\leftrightarrow"><span class='mathbtn' data-tex="\\leftrightarrow"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      for my $g (['\\alpha','alpha'],['\\beta','beta'],['\\gamma','gamma'],['\\varepsilon','epsilon']) {
        my ($ins,$srch)=@$g;
        print qq{<button type="button" class="pbtn hot" data-ins="$ins"><span class='mathbtn' data-tex="$ins"></span></button>};
      }
      print qq{<button type="button" class="pbtn hot" data-ins="\\lambda"><span class='mathbtn' data-tex="\\lambda"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\mu"><span class='mathbtn' data-tex="\\mu"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\sigma"><span class='mathbtn' data-tex="\\sigma"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\tau"><span class='mathbtn' data-tex="\\tau"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\chi^2"><span class='mathbtn' data-tex="\\chi^2"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn hot" data-ins="\\Delta"><span class='mathbtn' data-tex="\\Delta"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\Phi"><span class='mathbtn' data-tex="\\Phi"></span></button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\Omega"><span class='mathbtn' data-tex="\\Omega"></span></button>};
      print "</span>";

      print "</div>"; break();

      # Zeile 6: Funktionen, Fakultät/Binomial, Konstanten, Summen/Integrale, Sonstiges
      print "<div class='btnrow algebraRow tightRow'>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\sin\\left(#0\\right)">sin</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\cos\\left(#0\\right)">cos</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\tan\\left(#0\\right)">tan</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\arcsin\\left(#0\\right)">asin</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\arccos\\left(#0\\right)">acos</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\arctan\\left(#0\\right)">atan</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\exp\\left(#0\\right)">exp</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\ln\\left(#0\\right)">ln</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\log\\left(#0\\right)">log</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn hot" data-ins="#0!"><span class='mathbtn' data-tex="!"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn hot" data-ins="\\binom{#0}{#?}">
	      <span class="xmbinom"><span class="paren">(</span><span class="stack"><span>&#9633;</span><span>&#9633;</span></span><span class="paren">)</span></span>
	      </button>
      };
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn hot" data-ins="\\pi"><span class='mathbtn' data-tex="\\pi"></span></button>};
#      print qq{<button type="button" class="pbtn hot" data-ins="\\mathbf{e}^{#?}">e</button>};
      print qq{<button type="button" class="pbtn hot" data-ins="\\mathbf{e}">e</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\lim\\limits_\{n\\to\\infty\}">lim</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\int"><span class='mathbtn' data-tex="\\int"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\,\\text{d}"><span class='mathbtn' data-tex="\\,\\text{d}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sum"><span class='mathbtn' data-tex="\\sum"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\euro">€</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="\\%">%</button>};
      print qq{<button type="button" class="pbtn" data-ins="‰">‰</button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn dotsBtn" data-ins="\\ldots"><span class='mathbtn' data-tex="\\ldots"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn" data-ins="'"><span class='mathbtn' data-tex="'"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins='"'><span class='mathbtn' data-tex="``"></span></button>};
      print "</span>";

      print "<span class='algGrp'>";
      print qq{<button type="button" class="pbtn m" data-ins=".">.</button>};
      print qq{<button type="button" class="pbtn m" data-ins="{,}">,</button>};
      print qq{<button type="button" class="pbtn m" data-ins=";">;</button>};
      print "</span>";

      print "</div>"; break();

      # Zeile 7: Leerzeichen-Taste (mittleres Drittel, zentriert) + Navigations-/Editier-Icons (Spiegel von Zeile 1)
      print "<div class='btnrow bottomRow'>";
      print qq{<span class="navWrap"><button type="button" class="pbtn pbtn1 spacebar" data-ins="\\,"><span class="spaceGlyph">␣</span></button>$navicons</span>};
      print "</div>";

      # das Ende von der Palette

      # print qq(<hr />);
      print qq{<div id="ltx" class="lma ltx"></div>};
      print qq{<div id="mjs" class="lma mjs"></div>};
      
      # print qq(<hr />);
      
      print qq{<input type="hidden" name="user_latex" id="user_latex" value="">};
      print qq{<input type="hidden" name="user_mathjson" id="user_mathjson" value="">};
      print qq{<input type="hidden" name="richtig" id="richtig" value="">};

      # my $answer = $Common::cgi->param('answer');
      # print qq{<input type="hidden" name="answer" method="GET" id="answer" value="$answer">};

      print qq{</fieldset>};

      print qq{<div id="js_err" style="color:#a00; white-space:pre-wrap; font-size:14px;"></div>};

      print qq{ <script src="/js/abitur/prettyMathJSON.js"></script> };
      my $bwlJsV = (stat("/srv/wwwservers/www/tests/html/js/bwl/DOMContentLoaded.js"))[9] // time;
      print qq{ <script src="/js/bwl/DOMContentLoaded.js?v=$bwlJsV"></script> };
  } # Formel

  if ($kind ne 'formel') {
    print qq{<div class="sep"></div>};
    print qq{<button class="btn" type="submit" name="action" value="save">weiter</button>};
  }
  
  print end_form;  


  print qq{ 
    <script>
      function showSize() {
        document.getElementById("xysize").textContent = window.innerWidth+'×'+window.innerHeight; 
      }
      window.addEventListener ( "load" ,   showSize ); 
      window.addEventListener ( "resize" , showSize ); 
      document.addEventListener('DOMContentLoaded', showSize);

      document.addEventListener("DOMContentLoaded", function () {
          document.querySelectorAll(".mathbtn").forEach(function(el) { const tex = el.dataset.tex; if (tex) { katex.render ( tex, el, { throwOnError: false } ); } } )
        }
      );

    </script>
  };

      #       document.addEventListener("DOMContentLoaded", function () {
      #         document.querySelectorAll(".mathbtn").forEach(function(el) {
      #           const tex = el.dataset.tex;
      #           if (tex) { katex.render ( tex, el, { throwOnError: false } ); 
      #         }
      #         }  
      #       );

  HTML::page_footer();
  exit;
} # show_question - Ende
1;
