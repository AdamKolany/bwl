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

$action = $action ? $action : 'menu';

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
    </style>  
HEAD
print "</head>";

print "<body>";

my $chosen_kap = 'TSTA'; #'JuHa';
my $chosen_thm = $Common::cgi->param('thema')   // '';
my $menu=qq{
    <span style="display: block; margin-left: auto; text-align: right;">
      <a href='?action=menu' class='small' style='text-decoration: none; margin-left: 20px; '>Menu</a>
    </span>
  };

if ( $chosen_thm ne '' ) {

my $rows_themen =  $DB::dbh->selectall_arrayref( q{ select thema from themen where kapitel=? and th_kürzel=? }, undef, $chosen_kap, $chosen_thm  );
  
my $thema = $rows_themen->[0]->[0] // '';

  print qq{<div style="font-weight: bold; font-size: 2.2em;">$thema</div>};

  print $menu;

  print br();

  my $rows_fragen = 
      $DB::dbh->selectall_arrayref( q{ select frage, frage_id, status from fragen where kap_kürzel=? and th_kürzel=? order by frage_id}, undef, $chosen_kap, $chosen_thm  );
  

  print "<hr>";
  my $cnt=1; for my $r (@$rows_fragen) {
    my ($frage, $frage_id, $status) = @$r;

    next if $frage_id == 1100;

    printf "<div ><span style='font-weight: bold; color: #30863b;'>[ $thema: %02d ] (ID: $frage_id, Status: $status)</span>", $cnt;

    print $menu;

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

      # $antwort_mathjson = Common::htxt($antwort_mathjson);

      # print p({class=>'q'},  "<hr>LTX: " . ($antwort_latex) . "<hr>JSN: <br/>" . ($antwort_mathjson));
      
      print qq{<span style="color: #0000ff;"><hr>LTX: <br/><div class="ltxsrc" data-latex="$latex" style="text-align: center;">[…]</div></span>};
      # print qq{<span style="color: #7c4b24;"><hr>JSN: <br/><div class="jsnsrc" data-latex="$latex" style="text-align: center;">[…]</div></span>};
#      print qq{<span style="color: #7c4b24;"><hr>JSN: <br/><div class="jsnsrc" data-mjson="$mjson" style="text-align: center;">[…]</div></span>};
#      print qq{<span style="color: #aa00aa;"><hr>AST: <br/><div class="astsrc" data-latex="$latex" style="">[…]</div></span>};  
    };
    print "</div>";
    print "<hr>";
    $cnt++;
  }

  print $menu;

} else {  
  my $rows_thm = 
      $DB::dbh->selectall_arrayref( 
            q{ select th_kürzel, thema, cnt from (select kap_kürzel, th_kürzel,thema,count(frage_id) as cnt 
              from kapitel_themen_fragen group by kap_kürzel,th_kürzel,thema) where cnt>0 and kap_kürzel=? }, undef, $chosen_kap 
      );
  my @thm_values; my %thm_labels;
  if ($rows_thm && @$rows_thm) {
    @thm_values = (''); #my $r = pop @$rows_thm; $n_suggest= $$r[2]; $chosen_thm=$$r[0];
    %thm_labels = ( '' =>  ' -- Wähle das Thema -- '); # "$$r[1] ($chosen_thm: $n_suggest Fragen)" ); # 
    for my $r (@$rows_thm) {
      my ($code, $name,$cnt) = @$r;
      next unless defined $code;
      $name = '' unless defined $name;
      push @thm_values, $code;
      $thm_labels{$code} = "$name ($cnt Fragen)"; #"$name ($code)";
    }
  }

  if ($chosen_kap ne '' && @thm_values) {
    print start_form(-method=>'$method', -action=>$Common::SELF, -class=>'row');
    # print hidden(-name=>'debug', -value=>1) if $Common::cgi->param('debug');
    print hidden(-name=>'kapitel', -value=>$chosen_kap);
    print "Thema: ", 
      popup_menu( 
        -style => 'font-size: 1em; font-family: "TeX Gyre Bonus"; ',
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
//        el.innerHTML = json0;
    /*
      const dataset =el.dataset ; latex = prettyPrimes(dataset.latex) || ""; 
      latex = latex
        .replace(/\\\\(?:,|;|quad|qquad)\\b/g, ' ')
        .replace(/\\\\([bB]+ig+|left|right)\\b/g, ' ')
        .replace(/ {2,}/g, ' ') 
        .replace(/(\\d),(\\d)/g, '\$1.\$2')
        .replace(/(\\d){,}(\\d)/g, '\$1.\$2')
        .replace(/\\(\\s*([^()|]+)\\|([^()|]+)\\)/g, '(\$1,\$2)')
        ;
        
      const CE = new window.ComputeEngine.ComputeEngine(); 
      const json0 = JSON.stringify( CE.parse(latex, { form: 'raw'} ).json ).replace(/\"/g,"");      
    /* */
    /*
      const json1 = JSON.stringify( cleanMathJSON( json0 ), null, 2 ).replace(/\"/g,"");
      el.innerHTML = json0; // +'<hr/>'+'<span style="color: #572525;">'+json1+'</span>';
    /* */
    });
  </script>
};
  print qq{ <script src="/js/abitur/ast_katex.js"></script> };
  print qq{
  <script>
   
    document.querySelectorAll(".astsrc").forEach(function(el) {
      const dataset =el.dataset ; latex = prettyPrimes(dataset.latex) || ""; ast = latexToPrettyAST(latex); //latexAnswerToAST(latex);

      out = ast; //JSON.stringify(ast,null,16).replace(/\"/g,"");

      el.innerHTML = 
      '' // '<span style="text-align: center;">'+out+'</span>' + '<hr/><hr/>'
      + '<span style="color: #572525; white-space: pre-wrap; font-family: monospace; text-align: left;">'+out+'</span>';
    });
  /* */
  </script>
};

print "</body></html>";
