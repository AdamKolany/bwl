package show_result;

use CGI qw(:standard escapeHTML);
use utf8;
use strict;

require './Modules/Common.pm';
require './Modules/DB.pm';

# ============================================================
# Das Ergebniß
# ============================================================

sub run {
  Common::send_redirect(qs => "action=menu" . ($Common::cgi->param('debug') ? "&debug=1" : "")) unless $Common::sid;

  my ($total) = $DB::dbh->selectrow_array(q{SELECT COUNT(*) FROM geschichte WHERE sessionid = ?}, undef, $Common::sid);
  my ($good)  = $DB::dbh->selectrow_array(q{SELECT COUNT(*) FROM geschichte WHERE sessionid = ? AND richtig = 'J'}, undef, $Common::sid);
  $total ||= 0; $good ||= 0;

  my $pct = $total ? int(100 * $good / $total + 0.5) : 0;

  my $grade;
  if ($pct >= 95) { $grade = "1/S"; }
  elsif ($pct >= 80) { $grade = "2/G"; }  elsif ($pct >= 65) { $grade = "3/B"; }  elsif ($pct >= 50) { $grade = "4/A"; }  elsif ($pct >= 30) { $grade = "5/M"; } else { $grade = "6/U"; }

  HTML::page_header("Ergebniss");  Common::debug_block();
  print h2("Ergebniss"); print p("Richtig: $good / $total ($pct%)"); print p("Note: $grade");
  
  my $dbg = $Common::cgi->param('debug') ? "&debug=1" : "";
  print p( a({href=>"$Common::SELF?action=menu$dbg",  class=>'btn'   }, "Neues Thema/Kapitel"), "&nbsp;&nbsp;&nbsp;" );
  HTML::page_footer();  exit;
} # show_result - Ende

1;