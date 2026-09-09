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

# Firefox für Android hängt bei manchen Tablets trotzdem "Mobile" (statt
# "Tablet") in den User-Agent, sodass die reine UA-Prüfung dort fälschlich
# zuschlägt. Deshalb clientseitiger Ausweg: die Warnseite setzt selbst ein
# Cookie, sobald sie feststellt, dass der Bildschirm Tabletgröße hat
# (kürzere Kante >= 600 geräteunabhängige Pixel, Android "sw600dp"), oder
# der Nutzer per Knopf bestätigt. Liegt das Cookie vor, wird die Seite
# ganz normal ausgeliefert.
my $phone_bypass = ($ENV{'HTTP_COOKIE'} // '') =~ /(?:^|;\s*)notphone=1(?:\s*;|\s*$)/ ? 1 : 0;

if ($is_phone && !$phone_bypass) {
    print header(-type => 'text/html', -charset => 'UTF-8');
    print <<HTML;
<!DOCTYPE html>
<html lang="de">
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

.warn button {
  font-size: 1rem;
  padding: 0.6rem 1rem;
  margin-top: 1rem;
  cursor: pointer;
}

.debugline { color: gray; font-size: 0.7em; word-break: break-all; }
</style>
</head>
<body>

<div class="debugline"><span id="ua">$ua</span></div>
<div class="warn">
<h1>Achtung!!!</h1>
<p>Diese Seite ist nicht für die Nutzung auf Mobiltelefonen optimiert. Bitte verwenden Sie einen Desktop-Computer oder einen Laptop !!!</p>
<button type="button" id="notphone">Ich benutze ein Tablet oder einen Desktop &ndash; trotzdem fortfahren</button>
</div>

<script>
(function () {
  function bypass() {
    document.cookie = 'notphone=1; path=/; max-age=31536000; samesite=Lax';
    location.reload();
  }
  // Kürzere Bildschirmkante in geräteunabhängigen Pixeln: Telefone < 600,
  // Tablets >= 600. Firefox/Android meldet bei diesem Tablet trotzdem
  // "Mobile" im UA, daher hier die eigentliche Unterscheidung.
  var sw = Math.min(screen.width, screen.height);
  if (sw >= 600) { bypass(); return; }
  var ua = document.getElementById('ua');
  if (ua) ua.textContent = navigator.userAgent +
    ' [' + window.innerWidth + 'x' + window.innerHeight + ', sw=' + sw + ']';
  var btn = document.getElementById('notphone');
  if (btn) btn.addEventListener('click', bypass);
})();
</script>
</body>
</html>
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
