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
	 Link({ -rel => 'icon', -type => 'image/png', -sizes => '192x192', -href => '/js/bwl/favicon-ros6.png' }),
	 Link({ -rel => 'preconnect', -href => 'https://fonts.googleapis.com' }),
	 Link({ -rel => 'preconnect', -href => 'https://fonts.gstatic.com', -crossorigin => 'true' }),
	 Link({ -rel => 'stylesheet', -href => 'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400..700&display=swap' }),
	 Link({ -rel => 'stylesheet', -href => 'https://fonts.googleapis.com/css2?family=Platypi:ital,wght@0,300..800;1,300..800&display=swap' }),
    ],
    -bgcolor => '#808080',    -text    => '#000000',    -link    => '#A52A2A',    -vlink   => '#0000FF',    
);

my $bullet="<span style='font-size:50px;'>•</span>";

print qq{
<div id="titel" style="text-decoration: none; color: blue;">Mathematisieren und abstrahieren</div>
<div id="subtitel">$subtitle</div>
<ul id="menu" style="line-height:2vh;">
 <!-- <li>$bullet<a href="histmat/test.cgi" target="histmat"> Wissenstest zur Geschichte der Mathematik </a> -->
 <li>$bullet<a href="bwl/doit.cgi" target="bwl"> Mathematik für Betriebswirte (Test von dem Test)</a>
 <li>$bullet<a href="/filme/Tastatur-Schulung.mp4" target="film"> Einführungsvideo: Formeln eingeben mit der Bildschirmtastatur </a>
</ul>
};

print end_html;

