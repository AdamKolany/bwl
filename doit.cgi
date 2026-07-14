#!/usr/bin/perl

use open qw(:std :encoding(UTF-8));
binmode(STDOUT, ':encoding(UTF-8)');

use strict;
use utf8;

use CGI qw(:standard -utf8);
use CGI::Cookie;

require './Modules/HTML.pm';
require './Modules/Common.pm';
require './Modules/DB.pm';
require './Modules/show_menu.pm';
require './Modules/start_quiz.pm';
require './Modules/show_question.pm';
require './Modules/save_answer.pm';
require './Modules/show_result.pm';

my $ua = $ENV{'HTTP_USER_AGENT'} // '';

my $is_phone =
    (
        $ua =~ /iPhone|iPod|Windows Phone/i
        ||
        ($ua =~ /Android/i && $ua =~ /Mobile/i)
    )
    &&
    $ua !~ /iPad|Tablet|SM-X|SM-T/i
    ? 1 : 0;

if ($is_phone) {
    print header(-type => 'text/html', -charset => 'UTF-8');
    print header(-type => 'text/html', -charset => 'UTF-8');
    print <<HTML;
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Achtung!!!</title>
<style>
body {
  font-family: sans-serif;
  margin: 0;
  padding: 1rem;
  background: #f5f5f5;
}

.warn {
  box-sizing: border-box;
  width: min(100%, 40rem);
  margin: 2rem auto;
  padding: 1rem;
  border: 3px solid #a00;
  background: #fee;
}

.warn h1 {
  font-size: clamp(2rem, 8vw, 4rem);
  margin: 0 0 0.5rem 0;
}
</style>
</head>
<body>

<div style='color:gray; font-size: 0.7em;' class='debugline'><span id='ua'>$ua</span> [<script>document.write(window.innerWidth+'x'+window.innerHeight)</script>]</div>
<div class="warn">
<h1>Achtung!!!</h1>
<p>Diese Seite ist nicht für die Nutzung auf Mobiltelefonen optimiert. Bitte verwenden Sie einen Desktop-Computer oder einen Laptop !!!
</div>
</body>
</html>
<script>

document.addEventListener('DOMContentLoaded', function() {
  var target = document.getElementById('body');
  target.get = navigator.userAgent + ' [' + window.innerWidth + 'x' + window.innerHeight + ']';
});
\${'#ua'}.on('load', function(){ \${'#ua'}.text( navigator.userAgent + ' [' + window.innerWidth + 'x' + window.innerHeight + ']'); });

</script>
HTML
    exit;
}




# my $is_phone = ($ua =~ /iPhone|Android.+Mobile|Windows Phone|Mobile/i && $ua !~ /SM-X810|iPad/i ? 1 : 0 );
# my $is_phone = ($ua =~ /iPhone|Windows Phone|MobileQ/i ? 1 : 0 );
# if ($is_phone) {
# }

my $action = $Common::cgi->param('action'); $action = $action ? $action : 'menu';

if    ($action eq 'menu'   ){ show_menu::run();     }
elsif ($action eq 'start'  ){ start_quiz::run();    }
elsif ($action eq 'q'      ){ show_question::run(); }
elsif ($action eq 'save'   ){ save_answer::run();   }
elsif ($action eq 'result' ){ show_result::run();   }
elsif ($action eq 'reset'  ){ reset_session::run(); }
else  { die "Unknown action: $action"; }
