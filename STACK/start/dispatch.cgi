#!/usr/bin/perl

use strict;
use warnings;
use CGI qw(:standard);

print header(
    -charset       => 'utf-8',
    -type          => 'text/html',
    -expires       => 'now',
    -pragma        => 'no-cache',
    -cache_control => 'no-store, no-cache, must-revalidate, max-age=0',
);

my $subtitle = '';
if (open my $fh, '<', '.title') { chomp($subtitle = <$fh> // ''); close $fh;  }

print start_html(
    -title    => 'Mathematisieren und Abstrahieren',
    -lang     => 'de',
    -encoding => 'utf-8',
    -style    => { -src => '/css/bwl.css' },   # <-- /css/ako.css
        -head    => [
	 meta({ -http_equiv => 'Content-Type', -content => 'text/html; charset=UTF-8' }),
	 meta({ -http_equiv => 'content-language', -content => 'de' }),
	 meta({ -http_equiv => 'pragma', -content => 'no-cache' }),
	 Link({ -rel => 'icon', -type => 'image/png', -sizes => '192x192', -href => '/js/bwl/favicon-ptr1.png?v=1792878428' }),
	 Link({ -rel => 'preconnect', -href => 'https://fonts.googleapis.com' }),
	 Link({ -rel => 'preconnect', -href => 'https://fonts.gstatic.com', -crossorigin => 'true' }),
	 Link({ -rel => 'stylesheet', -href => 'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400..700&display=swap' }),
	 Link({ -rel => 'stylesheet', -href => 'https://fonts.googleapis.com/css2?family=Platypi:ital,wght@0,300..800;1,300..800&display=swap' }),
    ],
    -bgcolor => '#808080',    -text    => '#000000',    -link    => '#A52A2A',    -vlink   => '#0000FF',    
);

my $bullet="<span style='font-size:50px;'>•</span>";

print qq{
<style>
 #menu a, #menu a:visited { color: #0000FF; text-decoration: none; cursor: pointer; margin: 0 .4em; transition: color .15s, text-shadow .15s; }
 #menu a:hover, #menu a:focus { color: #4040FF; text-shadow: 0 0 6px rgba(255,255,255,.8); }
 #menu a:active { color: #000080; }
</style>
<div id="titel" style="text-decoration: none; color: blue;">Mathematisieren und Abstrahieren</div>
<div id="subtitel">$subtitle</div>
<!--
 <ul id="menu" style="line-height:2vh;">
  <li>$bullet<a href="./run-direct.cgi" target="direct">Direct</a>
  <li>$bullet<a href="./run-moodle.cgi" target="moodle">Moodle</a>
  <li>$bullet<a href="./run-ilias.cgi" target="iliass">Ilias</a>
 </ul>
-->
<div style="align:center; font-size:40px; text-decoration: none; color: blue; " id="menu">
 <a href="./run-direct.cgi" target="direct">Direct</a>&nbsp;&nbsp;&nbsp;
 <a href="./run-moodle.cgi" target="moodle">Moodle</a>&nbsp;&nbsp;&nbsp;
 <a href="./run-ilias.cgi" target="iliass">Ilias</a>
</div>
};

print end_html;

