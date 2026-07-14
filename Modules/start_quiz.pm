package start_quiz;

use CGI qw(:standard escapeHTML);
use utf8;
use strict;

require './Modules/Common.pm';
require './Modules/DB.pm';

sub run {
  my $kapitel = $Common::cgi->param('kapitel') // die "kein Kapitel";
  my $thema = $Common::cgi->param('thema') // die "kein Thema";

  my ($cnt) = $DB::dbh->selectrow_array(  q{SELECT count(*) FROM fragen WHERE "kap_kürzel" = ? AND "th_kürzel" = ? }, undef, $kapitel, $thema );
  $cnt ||= 0;

  my $n = $Common::cgi->param('n') // '';
  $n =~ s/^\s+|\s+$//g;

  if ($n !~ /^\d+$/ || $n < 1 || $n > $cnt) {
    my $dbg = $Common::cgi->param('debug') ? "&debug=1" : "";
    Common::send_redirect(qs => "action=menu&kapitel=$kapitel&thema=$thema&err=invalid_n$dbg");
  }

  my $cookie; if (!$Common::sid) { $Common::sid = Common::new_sid(); $cookie = Common::sid_cookie($Common::sid); }

  $DB::dbh->begin_work;
  $DB::dbh->do(q{INSERT INTO sessions(sessionid) VALUES (?) ON CONFLICT DO NOTHING}, undef, $Common::sid);
  $DB::dbh->do(q{DELETE FROM session_quiz WHERE sessionid = ?}, undef, $Common::sid);
  $DB::dbh->do(q{DELETE FROM session_questions WHERE sessionid = ?}, undef, $Common::sid);
  $DB::dbh->do(q{DELETE FROM geschichte WHERE sessionid = ?}, undef, $Common::sid);

  $DB::dbh->do(q{ INSERT INTO session_quiz(sessionid, kapitel, thema, n_questions) VALUES (?,?,?,?) }, undef, $Common::sid, $kapitel, $thema, $n);

  my $qids =
      $DB::dbh->selectcol_arrayref(
        q{ SELECT frage_id FROM fragen WHERE "kap_kürzel" = ? AND th_kürzel = ? ORDER BY random() LIMIT ?  }, undef, $kapitel, $thema, $n
      );
    # $DB::dbh->selectcol_arrayref(q{ SELECT frage_id FROM fragen WHERE "kap_kürzel" = ? AND th_kürzel = ? ORDER BY frage_id LIMIT ?  }, undef, $kapitel, $thema, $n);

  die "Keine Fragen zur Kapitel = $kapitel thema=$thema\n" unless @$qids;

  my $ins = $DB::dbh->prepare(q{ INSERT INTO session_questions(sessionid, nr, frage_id) VALUES (?,?,?) });

  my $nr0 = 1;  for my $qid (@$qids) { $ins->execute($Common::sid, $nr0++, $qid) if ($qid); }

  $DB::dbh->commit;

  my $dbg = $Common::cgi->param('debug') ? "&debug=1" : "";
  Common::send_redirect(qs => "action=q&nr=1$dbg", cookie => $cookie);
  
} # start_quiz - Ende

1;
