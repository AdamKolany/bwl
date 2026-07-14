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
			     
      print qq{<fieldset><legend>Antwort&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$richtig</legend>};
      
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
      <button type="button" class="pbtn" data-cmd="move_L">←</button>
      $skipp
      <button type="button" class="pbtn" data-cmd="move_R">→</button>
    </div>
  </div>
};

print qq{</div>};


     print qq{<div class="palette" style="margin-top:-30px;" id="palette">};

      my $actions=
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selectAll"><span style="font-size:0.75em;">★</span></button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="clear">⌧</button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selL"><span style="tiny">◀</span></button>}.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="selR"><span style="tiny">▶</span></button>}. $skipp.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="bs" >⌫</button>} . qq{<button type="button" class="pbtn pbtn1" data-cmd="del">⌦</button>}. $skipp.
        qq{<button type="button" class="pbtn pbtn1" data-cmd="undo">↺</button>} . qq{<button type="button" class="pbtn pbtn1" data-cmd="redo">↻</button>};

      my $capsel= qq{<button type="button" class="pbtn" data-cmd="capsel"><span class='m'>az ↔ AZ</span></button>} ;
      my $romGR=  qq{<button type="button" class="pbtn" data-cmd="romgr" ><span class='m'>az ↔ αζ</span></button>};    
      
      print $actions; 

      centered();  print $capsel; centered();      

      print qq{<button type="button" class="pbtn" data-ins="\\mathcal#0"><span class='mathbtn' data-tex="\\mathcal{C}"></span></button>};

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\mathbb#0"><span class='mathbtn' data-tex="\\mathbb{B}"></span></button>};
      
      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\mathfrak#0"><span class='mathbtn' data-tex="\\mathfrak{F}"></span></button>};

      centered(); print $romGR; centered(); 

      print $actions; 
      
      break(); toRight(); print "<div class='btnrow'>";

      for my $l ('a'  .. 'z') { print qq{<button type="button" class="pbtn" data-ins="$l">$l</button>}; }

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\,">␣</button>};      skipp(6);
      print qq{<button type="button" class="pbtn m" data-ins="{,}">,</button>};    skipp(3);
      print qq{<button type="button" class="pbtn m" data-ins=";">;</button>};      skipp(6);
      print qq{<button type="button" class="pbtn m" data-ins="\\ldots"><span class='mathbtn' data-tex="\\ldots"></span></button>};  skipp(6);
      for my $l ( 0   ..  9 ) { print qq{<button type="button" class="pbtn" data-ins="$l">$l</button>}; };
      
      print "</div>";toLeft(); break(); toRight();
      
      print "<div class='btnrow'>"; skipp(6); skipp(5);
      print "</div>";toLeft(); break(); toRight();print "<div class='btnrow'>";

      print qq{<button type="button" class="pbtn" data-ins="="><span class='mathbtn' data-tex="="></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\ne"><span class='mathbtn' data-tex="\\neq"></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\leqslant"><span class='mathbtn' data-tex="\\leqslant"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\geqslant"><span class='mathbtn' data-tex="\\geqslant"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="<"><span class='mathbtn' data-tex="<"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins=">"><span class='mathbtn' data-tex=">"></span></button>};

      skipp(4);

      print qq{<button type="button" class="pbtn" data-ins="\\approx"><span class='mathbtn' data-tex="\\approx"></span></button>};
      
      skipp(4);
      
      print qq{<button type="button" class="pbtn" data-ins="+"><span class='mathbtn' data-tex="+"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="-"><span class='mathbtn' data-tex="-"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="·"><span class='mathbtn' data-tex="\\cdot"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins=":"><span class='mathbtn' data-tex="\\colon"></span></button>};
      print qq{<button type="button" class="pbtn" style="position:center;" data-ins="\\frac{#0}{{#?}}">
	      <span class="xmfakefrac"> <span class="num">&#9633;</span><span class="slash">/</span><span class="den">&#9633;</span> </span>
	      </button>
      };

      print qq{<button type="button" class="pbtn" data-ins="\\cup"><span class='mathbtn' data-tex="\\cup"></span></button>}; 
      print qq{<button type="button" class="pbtn" data-ins="\\cap"><span class='mathbtn' data-tex="\\cap"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\bigcup"><span class='mathbtn' data-tex="\\bigcup"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\bigcap"><span class='mathbtn' data-tex="\\bigcap"></span></button>};      
      print qq{<button type="button" class="pbtn" data-ins="\\times"><span class='mathbtn' data-tex="\\times"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\setminus"><span class='mathbtn' data-tex="\\setminus"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt{#0}"><span class="m">√</span></button>}; # ▫
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[2]{#0}"><span class="m">²√</span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[3]{#0}"><span class="m">³√</span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sqrt[#?]{#0}"><span class="m">ⁿ√</span></button>};
      
      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="#0^2"><span class="xmsub"><span class="base">□</span><span class="sup">2</span></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^3"><span class="xmsub"><span class="base">□</span><span class="sup">3</span></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^{#?}"><span class="xmsub"><span class="base">□</span><span class="sup">m</span></span></button>};

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="#0_{#?}">
                  <span class="xmsub"><span class="base">□</span><span class="sub">m</span></span>
               </button>
              };
      print qq{<button type="button" class="pbtn" data-ins="#0^{#?}_{#?}">
                  <span class="xmsub"><span class="base">□</span><span class="sup">m</span><span class="sub">n</span></span>
               </button>
              };

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\overrightarrow{#0}"><span class="k-ovrarr" style="font-size:0.90em;">□</span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\overline{#0}"      ><span class="k-ovline" style="font-size:0.80em;">□</span></button>};


      print "</div>";toLeft(); break(); toRight();print "<div class='btnrow'>";

      skipp(6);      

      print qq{<button type="button" class="pbtn" data-ins="\\subseteq"><span class='mathbtn' data-tex="\\subseteq"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\subsetneq"><span class='mathbtn' data-tex="\\subsetneq"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\supseteq"><span class='mathbtn' data-tex="\\supseteq"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\supsetneq"><span class='mathbtn' data-tex="\\supsetneq"></span></button>};

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\in"><span class='mathbtn' data-tex="\\in"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\notin"><span class="mathbtn" data-tex="\\notin"></span></button> };

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\wedge"><span class='mathbtn' data-tex="\\wedge"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\vee"><span class='mathbtn' data-tex="\\vee"></span></button>};

      skipp(3);
      
      print qq{<button type="button" class="pbtn" data-ins="\\forall"><span class='mathbtn' data-tex="\\forall"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\exists"><span class='mathbtn' data-tex="\\exists"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\bigvee"><span class='mathbtn' data-tex="\\bigvee"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\bigwedge"><span class='mathbtn' data-tex="\\bigwedge"></span></button>};

      skipp(3);

      print qq{<button type="button" class="pbtn" data-ins="\\Rightarrow"><span class='mathbtn' data-tex="\\Rightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\rightarrow"><span class='mathbtn' data-tex="\\rightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\Longrightarrow"><span class='mathbtn' data-tex="\\Longrightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\longrightarrow"><span class='mathbtn' data-tex="\\longrightarrow"></span></button>};
      skipp(3);
      print qq{<button type="button" class="pbtn" data-ins="\\Leftrightarrow"><span class='mathbtn' data-tex="\\Leftrightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\leftrightarrow"><span class='mathbtn' data-tex="\\leftrightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\Longleftrightarrow"><span class='mathbtn' data-tex="\\Longleftrightarrow"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\longleftrightarrow"><span class='mathbtn' data-tex="\\longleftrightarrow"></span></button>};
      skipp(3);
      print qq{<button type="button" class="pbtn" data-ins="\\equiv"><span class='mathbtn' data-tex="\\equiv"></span></button>};
      skipp(3);
      print qq{<button type="button" class="pbtn" data-ins="\\neg"><span class='mathbtn' data-tex="\\neg"></span></button>};
      skipp(3);
      print qq{<button type="button" class="pbtn" data-ins="\\sim"><span class='mathbtn' data-tex="\\sim"></span></button>};

      skipp(6);

      print "</div>";toLeft(); break(); toRight();print "<div class='btnrow'>";

      print qq{<button type="button" class="pbtn" data-ins="\\big(#?\\big|\#0\\big)"><span class='mathbtn' data-tex="(\\cdot|\\cdot)"></span></button>};
      
      skipp(6);      

      print qq{<button type="button" class="pbtn m" data-ins="\\infty"><span class='mathbtn' data-tex="\\infty"></span></button>};   skipp(3);
      print qq{<button type="button" class="pbtn m" data-ins="\\aleph_0"><span class='mathbtn' data-tex="\\aleph"></span></button>}; skipp(3);
      print qq{<button type="button" class="pbtn m" data-ins="\\varnothing"><span class='mathbtn' data-tex="\\varnothing"></span></button>}; 
      
      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\left(#0\\right)"><span class='mathbtn tr' data-tex="\\left(\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left[#0\\right]"><span class='mathbtn tr' data-tex="\\left[\\cdot\\right]"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left\\{#0\\right\\}"><span class='mathbtn tr' data-tex="\\left\\{\\cdot\\right\\}"></span></button>};
      
      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\left\\langle#0\\,,\\;#?\\right\\rangle"><span class='mathbtn tr' data-tex="\\left\\langle\\cdot\\,,\\;\\cdot\\right\\rangle"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left(#0\\,,\\;#?\\right)"><span class='mathbtn tr' data-tex="\\left(\\cdot\\,,\\;\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left[#0\\,,\\;#?\\right]"><span class='mathbtn tr' data-tex="\\left[\\cdot\\,,\\;\\cdot\\right]"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left[#0\\,,\\;#?\\right)"><span class='mathbtn tr' data-tex="\\left[\\cdot\\,,\\;\\cdot\\right)"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left(#0\\,,\\;#?\\right]"><span class='mathbtn tr' data-tex="\\left(\\cdot\\,,\\;\\cdot\\right]"></span></button>};
      
      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\left\\{#0:\\,#?\\right\\}"><span class='mathbtn tr' data-tex="\\left\\{\\cdot:\\,\\ldots\\right\\}"></span></button>};

      skipp(3);

      print qq{<button type="button" class="pbtn" data-ins="\\left((#0,#0)\\mapsto#?\\right)"><span class='mathbtn' data-tex="\\mapsto"></span></span></button>};

      print qq{<button type="button" class="pbtn" data-ins="\\int"><span class='mathbtn' data-tex="\\int"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\sum"><span class='mathbtn' data-tex="\\sum"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\prod"><span class='mathbtn' data-tex="\\prod"></span></button>};

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{C}"><span class='mathbtn' data-tex="\\mathbb{C}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{R}"><span class='mathbtn' data-tex="\\mathbb{R}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{Q}"><span class='mathbtn' data-tex="\\mathbb{Q}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{Z}"><span class='mathbtn' data-tex="\\mathbb{Z}"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbb{N}"><span class='mathbtn' data-tex="\\mathbb{N}"></span></button>};
      


      skipp(6);

      print "</div>";toLeft(); break(); toRight();print "<div class='btnrow'>";
      
      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\imath"><span class='mathbtn' data-tex="\\imath"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="\\left|#0\\right|"><span class='mathbtn' data-tex="\\left|\\cdot\\right|"></span></button>};

      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\sin\\left(#0\\right)">sin</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\cos\\left(#0\\right)">cos</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\tan\\left(#0\\right)">tan</button>};
      
      skipp(3);
      
      print qq{<button type="button" class="pbtn" data-ins="\\arcsin\\left(#0\\right)">asin</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\arccos\\left(#0\\right)">acos</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\arctan\\left(#0\\right)">atan</button>};
      
      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\ln\\left(#0\\right)">ln</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\log\\left(#0\\right)">log</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\exp\\left(#0\\right)">exp</button>};
            
      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\lim\\limits_\{n\\to\\infty\}">lim</button>};
      
      print qq{
              <button type="button" class="pbtn" data-ins="\\xrightarrow[#0\\to#?]{}"> <span class='mathbtn tr' data-tex="\\xrightarrow[n\\to\\infty]{}"></span>
                <!--span style="font-size: 0.6em; padding: 5px 2px 5px 2px;">[n→∞]</span-->
                <!--span class="mathbtn">\\(\\xrightarrow[n\\to\\infty]{}\\)</span--><!--img src="/images/abitur/arrow_n_to_infinity.png" alt="n→∞" class="btnimg"-->
              </button>
            };

      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="\\mathbf{Rg}\\left(#0\\right)">Rg</button>};
      print qq{<button type="button" class="pbtn" data-ins="\\mathbf{Dm}\\left(#0\\right)">Dm</button>};

      skipp(6);
      
      print qq{<button type="button" class="pbtn" data-ins="\\pm"><span class='mathbtn' data-tex="\\pm"></span></button>};


      skipp(6);

      print qq{<button type="button" class="pbtn" data-ins="'"><span class='mathbtn' data-tex="'"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins='"'><span class='mathbtn' data-tex="``"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^\\circ"><span class='mathbtn' data-tex="{}^\\circ"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^\\ast"><span class='mathbtn' data-tex="{}^\\ast"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^\\top"><span class='mathbtn' data-tex="{}^\\top"></span></button>};
      print qq{<button type="button" class="pbtn" data-ins="#0^\\dagger"><span class='mathbtn' data-tex="{}^\\dagger"></span></button>};
      skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\circ"><span class='mathbtn' data-tex="\\circ"></span></button>};
      skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\big|"><span class='mathbtn' data-tex="\\big|"></span></button>}; 
      print qq{<button type="button" class="pbtn" data-ins="\\big\\|"><span class='mathbtn' data-tex="\\big\\|"></span></button>}; 

      skipp(6);
      
      print "</div>";toLeft(); break(); toRight();
      
      
      print "<div class='btnrow'>";  print "</div>";

      toLeft(); break(); 

      print $actions; 
      
      toRight();  print $capsel; centered();      

      print qq{<button type="button" class="pbtn" data-ins="\\ell"><span class='mathbtn' data-tex="\\ell"></span></button>} ;               skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\epsilon"><span class='mathbtn' data-tex="\\epsilon"></span></button>} ;       skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\varepsilon"><span class='mathbtn' data-tex="\\varepsilon"></span></button>} ; skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\phi"><span class='mathbtn' data-tex="\\phi"></span></button>} ;               skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\tau"><span class='mathbtn' data-tex="\\tau"></span></button>} ;               skipp(6);
      print qq{<button type="button" class="pbtn" data-ins="\\theta"><span class='mathbtn' data-tex="\\theta"></span></button>} ;

      centered(); print $romGR; toRight(); 

      print $actions; 
      
      print qq{</div>}; 


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
      print qq{ <script src="/js/abitur/DOMContentLoaded.js"></script> };
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
