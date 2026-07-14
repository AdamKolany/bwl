package Common;

use strict;
use CGI;

# ============================================================
# KONFIGURATION
# ============================================================

our $DEFAULT_N = 3;

our $DB='bwl'; our $passwd="=jha_MUA@19850928//#DB,\L$DB"; our $user='drak'; our $THEMA='TSTA';

sub escape_html {
  return CGI::escapeHTML($_[0] // '');
}

#my $render = \&escape_html;
our $render = \&render_rich;

# Lokal MathJax v4 
# our $MATHJAX_JS_URL = "/js/mathjax4/tex-mml-chtml.js";

# ============================================================
# CGI
# ============================================================
our $cgi  = CGI->new; my $SELF = $cgi->url(-relative => 1);

# ============================================================
# Session cookie
# ============================================================
our %cookies = CGI::Cookie->fetch;
our $sid = $cookies{SID} ? $cookies{SID}->value : undef;
sub new_sid    {  my @c = ('A'..'Z','a'..'z',0..9), my $s='';  $s .= $c[int rand @c] for 1..18; return $s; }
sub sid_cookie {  my ($s) = @_; return CGI::Cookie->new( -name     => 'SID',  -value    => $s, -path     => '/',  -httponly => 1, ); }
sub send_redirect {
  my (%opt) = @_;  my $qs = $opt{qs} // die "redirect: no qs"; my $cookie = $opt{cookie}; my $uri = $SELF . "?" . $qs;
  print $cookie ? $cgi->redirect(-uri => $uri, -cookie => $cookie) : $cgi->redirect(-uri => $uri); exit;
}

sub render_rich {
  my ($raw) = @_; $raw //= '';
  my $out = '';  my $i = 0;
  while ($raw =~ /\[\[img:\s*([^\]\r\n]+?)\s*\]\]/g) {
    my $mstart = $-[0]; my $mend = $+[0]; my $spec = $1;
    $out .= CGI::escapeHTML(substr($raw, $i, $mstart - $i));
    my @parts = split(/\|/, $spec);
    my $src = shift(@parts) // '';
    $src =~ s/^\s+|\s+$//g;
    my $align = 'center';    my $w_px;    my $pct;    my $cap;
    for my $p (@parts) {
      $p //= ''; $p =~ s/^\s+|\s+$//g; next if $p eq '';
      my $pl = lc($p);
      if ($pl eq 'left' || $pl eq 'center' || $pl eq 'right') {        $align = $pl; next;      }
      if ($pl =~ /^w\s*=\s*(\d{1,4})$/) {        $w_px = $1; next;      }
      if ($pl =~ /^(pct|percent)\s*=\s*(\d{1,3})$/) {        my $v = $2; $v = 100 if $v > 100;        $pct = $v; next;      }
      if ($p =~ /^cap\s*=\s*(.*)\z/s) {        $cap = $1; $cap =~ s/^\s+|\s+$//g; next;      }
    }

    if ($src =~ m{\A/abitur/(img|images)/[A-Za-z0-9._/-]+\.(png|jpg|jpeg|gif|webp)\z}i) {
      my $src_attr = CGI::escapeHTML($src); my $style = '';
      if (defined $pct) { $style = qq{ style="width:$pct%;"}; } elsif (defined $w_px) { $style = qq{ style="width:${w_px}px;"}; }
      my $img = qq{<img class="qimg" src="$src_attr" alt="" loading="lazy" decoding="async">};
      # outer robi align, inner ma width + caption
      if (defined $cap && $cap ne '') {
        my $cap_html = CGI::escapeHTML($cap);
        $out .= qq{<div class="imgouter $align"><figure class="imgbox"$style>$img<figcaption class="imgcap">$cap_html</figcaption></figure></div>};
      } else {
        $out .= qq{<div class="imgouter $align"><div class="imgbox"$style>$img</div></div>};
      }
    } else { $out .= CGI::escapeHTML("[[img:$spec]]"); }
    $i = $mend;
  } # while img
  $out .= CGI::escapeHTML(substr($raw, $i));
  # $out =~ s/\\\\/<br\/>/g; 
  # $out =~ s/\\cr/\\\\/g; 
  $out =~ s/\\br/<br\/>/g; 

  $out =~ s/\\quad/&nbsp;/g; $out =~ s/\\qquad/&nbsp;&nbsp;/g; $out =~ s/\\qqquad/&nbsp;&nbsp;&nbsp;/g;
  return $out;
} # render_rich

# ============================================================
# Fragestatus:
#   E = Einzel (eine richtige Antwort)
#   M = Multi  (mehrere richtige Antworten)
#   O = Open   (Freitext)
#   F = Formel (MathLive; Bewertung über MathJSON)
# ============================================================
sub status_kind {
  my ($s) = @_;
  $s = '' unless defined $s;
  $s =~ s/^\s+|\s+$//g;
  return 'single'  if $s eq 'E';
  return 'multi'   if $s eq 'M' || $s eq 'W';   # W: alte Daten (falls vorhanden)
  return 'open'    if $s eq 'O';
  return 'formel'  if $s eq 'F';
  die "Unbekannter Fragestatus='$s' (erwartet: E/M/O/F)\n";
}
sub is_multi_status {  my ($s) = @_;  return status_kind($s) eq 'multi' ? 1 : 0; }
sub norm_text {  my ($s) = @_;  $s = '' unless defined $s;  $s =~ s/\r\n/\n/g;  $s =~ s/^\s+|\s+$//g;  $s =~ s/\s+/ /g;  $s = lc($s);  return $s; }


sub debug_block {
  return unless $Common::cgi->param('debug');
  print CGI::h3("DEBUG<");
  print CGI::p("REQUEST_METHOD=" . ($ENV{REQUEST_METHOD}//''));
  print CGI::p("\$Common::SELF=" . $Common::SELF);
  print CGI::p("SID(cookie)=" . (defined $Common::sid ? $Common::sid : '(none)'));
  print CGI::p("action values: " . join(", ", $Common::cgi->param('action')));
  my $txt = "";
  for my $n ($Common::cgi->param) {
    my @v = $Common::cgi->param($n);
    $txt .= "$n = [" . join(", ", map { defined $_ ? $_ : 'undef' } @v) . "]\n";
  }
  print CGI::pre($Common::render->($txt));
  print qq{<div class="sep"></div>};
}

# Escape HTML, ale zostawiamy $...$ (MathJax sobie z tym poradzi)
sub htxt {  my ($s) = @_;  $s = '' unless defined $s;  return $Common::render->($s); }


1;
