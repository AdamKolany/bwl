#!/usr/bin/perl

use open qw(:std :encoding(UTF-8));
binmode(STDOUT, ':encoding(UTF-8)');

use strict;
use utf8;

use CGI qw(:standard -utf8);
use CGI::Cookie;

use JSON::PP qw(decode_json encode_json);

require './Modules/HTML.pm';
require './Modules/Common.pm';
require './Modules/DB.pm';
require './Modules/show_menu.pm';
require './Modules/start_quiz.pm';

my $method='GET';

my $action = $Common::cgi->param('action');
$action = $action ? $action : '';

# ============================================================
# Speichern (Frage + Antworten) - vor jeder Ausgabe, damit ein
# Redirect (Post/Redirect/Get) moeglich ist
# ============================================================
if ($action eq 'save') {
  my $frage_id = $Common::cgi->param('frage_id') // die "no frage_id";
  $frage_id =~ s/\D//g;
  die "no frage_id" unless $frage_id;

  my $chosen_thm = $Common::cgi->param('thema') // '';
  my $frage_text = $Common::cgi->param('frage_text') // '';
  my $status     = $Common::cgi->param('status') // '';
  $status =~ s/^\s+|\s+$//g;
  die "Unbekannter Status='$status' (erwartet: E/M/O/F)\n" unless $status =~ /^[EMOF]$/;

  $DB::dbh->begin_work;

  $DB::dbh->do(q{ UPDATE fragen SET frage=?, status=? WHERE frage_id=? }, undef, $frage_text, $status, $frage_id);

  my $aids = $DB::dbh->selectcol_arrayref(q{ SELECT antwort_id FROM antworte WHERE frage_id=? ORDER BY antwort_id }, undef, $frage_id);
  for my $aid (@$aids) {
    my $atext   = $Common::cgi->param("antwort_$aid") // '';
    my $alatex  = $Common::cgi->param("latex_$aid")   // '';
    my $richtig = $Common::cgi->param("richtig_$aid") ? 'J' : 'N';
    $DB::dbh->do(
      q{ UPDATE antworte SET antwort=?, antwort_latex=NULLIF(?, ''), richtig=? WHERE antwort_id=? },
      undef, $atext, $alatex, $richtig, $aid
    );
  }

  $DB::dbh->commit;

  my $dbg = $Common::cgi->param('debug') ? '&debug=1' : '';
  Common::send_redirect(qs => "thema=$chosen_thm&saved=$frage_id$dbg");
}

print $Common::cgi->header(-type => 'text/html; charset=UTF-8', -Cache_Control => 'no-store, no-cache, must-revalidate, max-age=0',  -Pragma        => 'no-cache',  -Expires       => '0',);
print "<!DOCTYPE html><html lang='de'><head>";
print <<HEAD;
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/js/mathlive/mathlive-fonts.css">
    <link rel="stylesheet" href="/js/mathlive/mathlive-static.css">
    <link rel="stylesheet" href="/css/abitur/katex.min.css">
    <script src="/js/compute-engine.min.umd.js?v=0.53.0"></script>
    <script src="/js/katex.min.js"></script>
    <script src="/js/abitur/LTX2JSN.js"></script>

    <!--script src="/js/abitur/prettyMathJSON.js"></script-->
    <!--script src="/js/abitur/LTX2AST.js"></script-->

    <script src="/js/abitur/parseLatex2AST.js"></script>

    <script defer src="/js/mathjax4/tex-mml-chtml.js"></script>
    <script>
      window.MathJax = {
        output: {  scale: 1.10, minScale: 1.0 },  // <- math font
        tex: { inlineMath: [['\\\\(','\\\\)'], ['\$', '\$']], displayMath: [['\\\\[','\\\\]']], processEscapes: true },
        options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] },
        startup: { pageReady: () => {return MathJax.startup.defaultPageReady().then(() => {const el = document.getElementById('mathwrap'); if (el) el.classList.remove('mjx-hide');}); } }
      };
      document.fonts?.load('italic 16px "KaTeX_Math"'); ["1","2","3","4"].forEach(n => document.fonts?.load(`16px "KaTeX_Size\${n}"`));
    </script>
    <style>
      html, body { height: 100%; margin: 0; }
      body { min-height: 100vh;    display: inline-box;    align-items: center;    justify-content: center;    padding: 10%;    box-sizing: border-box; font-size: 1.5em;  }
      .pagebox{ width: 100%; max-width: 95vw; position: static; margin-top: 0px;  }
      .astsrc {
        font-family: "KaTeX_Math", "Times New Roman", serif; font-size: 0.9em;
        color: #e67224; background-color: #f3e4e4;
        padding: 10px; border-radius: 5px; margin: 0px;
      }
      .q { font-size: 1.1em; }
      .editform { font-size: 0.6em; background: #f6f6f6; border: 1px solid #ccc; border-radius: 6px; padding: 10px; margin: 10px 0; }
      .editform .editq { width: 96%; font-size: 1.1em; font-family: inherit; }
      .editans { display: flex; align-items: center; gap: 6px; margin: 4px 0; }
      .editans input[type="text"] { font-size: 1em; }
      .editans .a-text { width: 30%; }
      .editans .a-latex { width: 50%; }
      .savemsg { color: #30863b; font-weight: bold; margin-left: 10px; }
    </style>
HEAD
print "</head>";

print "<body>";

my $chosen_kap = 'TSTA'; #'JuHa';
my $chosen_thm = $Common::cgi->param('thema') // '';
my $saved_id   = $Common::cgi->param('saved') // '';

my $rows_thm =
    $DB::dbh->selectall_arrayref(
          q{ select th_kürzel, thema, cnt from (select kap_kürzel, th_kürzel,thema,count(frage_id) as cnt
            from kapitel_themen_fragen group by kap_kürzel,th_kürzel,thema) where cnt>0 and kap_kürzel=? }, undef, $chosen_kap
    );
my @thm_values; my %thm_labels;

my ($max_thema_len) = $DB::dbh->selectrow_array(q{ SELECT max(length(thema)) FROM themen });
my $band = int($max_thema_len/2);
# $max_thema_len -= length(' -- Wähle das Thema -- ');

if ($rows_thm && @$rows_thm) {
  @thm_values = ('');
  %thm_labels = ( '' =>  ( (' 'x$band) . ' -- Wähle das Thema -- '. (' 'x$band ) ) );
  for my $r (@$rows_thm) {
    my ($code, $name,$cnt) = @$r;
    next unless defined $code;
    $name = '' unless defined $name;
    push @thm_values, $code;
    $thm_labels{$code} = "$name ($cnt Fragen)";
  }
}

my $thema_picker =
    start_form(-method=>'$method', -action=>$Common::SELF, -style=>'display:inline-block;')
  . hidden(-name=>'kapitel', -value=>$chosen_kap)
  . popup_menu(
      -style => 'font-size: 0.9em; font-family: "TeX Gyre Bonus";',
      -name=>'thema', -values  => \@thm_values, -labels   => \%thm_labels, -default  => '', -override => 1,
      -onchange => 'this.form.submit()'
    )
  . end_form;

my $menu=qq{
    <span style="display: block; margin-left: auto; text-align: right;">
      $thema_picker
    </span>
  };

if ( $chosen_thm ne '' ) {

my $rows_themen =  $DB::dbh->selectall_arrayref( q{ select thema from themen where kapitel=? and th_kürzel=? }, undef, $chosen_kap, $chosen_thm  );

my $thema = $rows_themen->[0]->[0] // '';

  print qq{<div style="font-weight: bold; font-size: 2.2em;">$thema</div>};


  print br();

  my $rows_fragen =
      $DB::dbh->selectall_arrayref( q{ select frage, frage_id, status from fragen where kap_kürzel=? and th_kürzel=? order by frage_id}, undef, $chosen_kap, $chosen_thm  );

  print "<hr>";
  my $cnt=1; for my $r (@$rows_fragen) {
    my ($frage, $frage_id, $status) = @$r;

    next if $frage_id == 1100;

    printf "<div ><span style='font-weight: bold; color: #30863b;'>[ $thema: %02d ] (ID: $frage_id, Status: $status)</span>", $cnt;

    print $menu;

    if ($saved_id ne '' && $saved_id == $frage_id) {
      print qq{<span class="savemsg">Gespeichert!</span>};
    }

    print "<br /><span class='q' style='color: #510c6d;'>", Common::htxt($frage), "</span>";
    print "</div>";

    my $rows_antwort =
        $DB::dbh->
          selectall_arrayref(
            q{ select antwort_id, antwort, antwort_text, antwort_latex, antwort_mathjson from antworte  where frage_id=? order by antwort_id}, undef, $frage_id
          );
    print "<div style='color: #3a59c0;'>";
    for my $r (@$rows_antwort) {
      my ($antwort_id, $antwort, $antwort_text, $antwort_latex, $antwort_mathjson) = @$r; my $latex0 = $antwort_latex;

      my $latex = Common::htxt($latex0);

      my $mjson = Common::htxt($antwort_mathjson // '');

      $antwort_latex="\\[$antwort_latex\\]" if defined $antwort_latex && $antwort_latex ne '';

      print qq{<span style="color: #0000ff;"><hr>LTX: <br/><div class="ltxsrc" data-latex="$latex" style="text-align: center;">[…]</div></span>};
    };
    print "</div>";

    # --------------------------------------------------------
    # Bearbeitungsformular
    # --------------------------------------------------------
    print qq{<div class="editform">};
    print start_form(-method=>'POST', -action=>$Common::SELF);
    print hidden(-name=>'action', -value=>'save');
    print hidden(-name=>'frage_id', -value=>$frage_id);
    print hidden(-name=>'thema', -value=>$chosen_thm);
    print hidden(-name=>'debug', -value=>1) if $Common::cgi->param('debug');

    print qq{<div><b>Frage:</b><br/>};
    print qq{<textarea class="editq" name="frage_text" rows="3">} . CGI::escapeHTML($frage // '') . qq{</textarea></div>};

    print qq{<div><b>Status:</b> };
    print popup_menu(
      -name=>'status_display',
      -values => ['E','M','O','F'],
      -labels => { E=>'E – Einzelauswahl', M=>'M – Mehrfachauswahl', O=>'O – Freitext', F=>'F – Formel' },
      -default=> $status,
      -disabled=>1,
    );
    print hidden(-name=>'status', -value=>$status);
    print qq{</div>};

    print qq{<div><b>Antworten:</b></div>};
    for my $r (@$rows_antwort) {
      my ($antwort_id, $antwort, $antwort_text, $antwort_latex, $antwort_mathjson) = @$r;
      my $richtig = $DB::dbh->selectrow_array(q{ select richtig from antworte where antwort_id=? }, undef, $antwort_id);
      my $chk = (defined $richtig && $richtig eq 'J') ? 'checked' : '';
      print qq{<div class="editans">};
      print qq{<label><input type="checkbox" disabled $chk> richtig</label>};
      print hidden(-name=>"richtig_$antwort_id", -value=>1) if $chk;
      print qq{<input type="text" class="a-text" value="} . CGI::escapeHTML($antwort // '') . qq{" placeholder="Antworttext" disabled>};
      print hidden(-name=>"antwort_$antwort_id", -value=>$antwort // '');
      print qq{<input type="text" class="a-latex" name="latex_$antwort_id" value="} . CGI::escapeHTML($antwort_latex // '') . qq{" placeholder="LaTeX">};
      print qq{</div>};
    }

    print qq{<button class="btn" type="submit" style="margin-top:8px;">Speichern</button>};
    print end_form;
    print qq{</div>};

    print "<hr>";
    $cnt++;
  }

} else {
  if ($chosen_kap ne '' && @thm_values) {
    print "<div style='display: flex; flex-direction: row; align-items: center; justify-content: center; margin-top:10%;'>";
    print start_form(-method=>'$method', -action=>$Common::SELF, -class=>'row');
    print hidden(-name=>'kapitel', -value=>$chosen_kap);
    print "Thema: <br>",
      popup_menu(
        -style => 'font-size: 1em; font-family: "TeX Gyre Bonus"; margin-left: 5.0em; margin-top: 1.0em;',
        -name=>'thema', -values  => \@thm_values, -labels   => \%thm_labels, -default  => $chosen_thm, -onchange => 'this.form.submit()' ), br();
    print qq{<div class="sep"></div>};

    print end_form;
    print "</div>";
  }
}

print qq{ <script src="/js/abitur/prettyPrimes.js"></script> };

print qq{
  <script>
    document.querySelectorAll(".ltxsrc").forEach( function(el) {
      const dataset =el.dataset ; latex0 = dataset.latex || "";
      latex = latex0.replace(/(\\d),(\\d)/g, '\$1{,}\$2')
              .replace(/\\\\([bB]+ig+|left|right)\\b/g, ' ')
              .replace(/\\(\\s*([^()|]+)\\|([^()|]+)\\)/g, '(\$1,\$2)');
      el.innerHTML = '\\\\[' + latex0 + '\\\\]'+'<hr/>'
                             + latex  ;
    });
  </script>
};

print qq{
  <script>
    document.querySelectorAll(".jsnsrc").forEach(function(el) {
        const dataset = el.dataset;
        const json0 = dataset.mjson || "";
        el.textContent = json0;
    });
  </script>
};
  print qq{ <script src="/js/abitur/ast_katex.js"></script> };
  print qq{
  <script>

    document.querySelectorAll(".astsrc").forEach(function(el) {
      const dataset =el.dataset ; latex = prettyPrimes(dataset.latex) || ""; ast = latexToPrettyAST(latex);

      out = ast;

      el.innerHTML =
      ''
      + '<span style="color: #572525; white-space: pre-wrap; font-family: monospace; text-align: left;">'+out+'</span>';
    });
  /* */
  </script>
};

print "</body></html>";
