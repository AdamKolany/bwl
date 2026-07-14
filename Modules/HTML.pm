package HTML;

use strict;
use CGI qw(:standard escapeHTML);

sub page_header {
  my ($title) = @_;
  my $console = param('console') ? qq{<script src="/js/eruda.min.js"></script><script>try{ eruda.init(); }catch(e){}</script>}:'';
  my $head = <<HEAD;
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="UTF-8"> $console
    <link rel="stylesheet" href="/js/mathlive/mathlive-fonts.css">
    <link rel="stylesheet" href="/js/mathlive/mathlive-static.css">
    <!-- <script defer src="https://cdn.jsdelivr.net/npm/katex\@0.16.11/dist/katex.min.js"></script> -->

    <link rel="stylesheet" href="/css/abitur/katex.min.css">
    <script defer src="/js/katex.min.js"></script>
    <script defer src="/js/abitur/ast_katex.js"></script>
    
    <script defer src="/js/compute-engine.min.umd.js?v=0.53.0"></script>

    <script defer src="/js/mathlive/mathlive.js"></script>

    <link rel="stylesheet" href="/css/abitur/Abitur.css">
    <script src="/js/abitur/Initialize.js"></script>
    <script src="/js/abitur/auxFunctions.js"></script>
    <script defer src="/js/abitur/topLevelNormalization.js"></script>

    <script>
    
      window.MathJax = {
        output: {  scale: 1.10, minScale: 1.0 },  // <- math font
        tex: { inlineMath: [['\\\\(','\\\\)'], ['\$', '\$']], displayMath: [['\\\\[','\\\\]']], processEscapes: true },
        options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] },
        startup: { pageReady: () => {return MathJax.startup.defaultPageReady().then(() => {const el = document.getElementById('mathwrap'); if (el) el.classList.remove('mjx-hide');}); } }
      };
      
      setTimeout(() => { const el = document.getElementById('mathwrap'); if (el) el.classList.remove('mjx-hide'); }, 500  ) ;
      
      window.__canonMathJSONFromLatex = function(latex) {
        try {
          if (!window.ComputeEngine) return null;
          const ce = new window.ComputeEngine.ComputeEngine();
          const expr = ce.parse(latex || '');
          return expr ? expr.json : null;
        } catch (e) { return null; }
      };
      
    </script>

    <script defer src="/js/mathjax4/tex-mml-chtml.js"></script>
    <script>      
      window.__canonMathJSONFromLatex = function(latex) {
        try {
          if (!window.ComputeEngine) return null;
          const ce = new window.ComputeEngine.ComputeEngine();
          const expr = ce.parse(latex || '');
          return expr ? expr.json : null;
        } catch (e) { return null; }
      };      
    </script>
HEAD

  print $Common::cgi->header(-type => 'text/html; charset=UTF-8', -Cache_Control => 'no-store, no-cache, must-revalidate, max-age=0',  -Pragma        => 'no-cache',  -Expires       => '0',);

  print "<!DOCTYPE html><html lang='de'><head>$head</head><body><div class='box'><div id='mathwrap' class='mjx-hide'>";

}

sub page_footer {  print qq{</div></div>}, end_html; }

1;
