package save_answer;

use CGI qw(:standard escapeHTML);
use utf8;
use strict;

require './Modules/Common.pm';
require './Modules/DB.pm';

# ============================================================
# Speichern einer Antwort
# ============================================================
sub run {
  Common::send_redirect(qs => "action=menu" . ($Common::cgi->param('debug') ? "&debug=1" : "")) unless $Common::sid;

  my $nr  = $Common::cgi->param('nr')  // die "no nr";    $nr  =~ s/\D//g;
  my $qid = $Common::cgi->param('qid') // die "no qid";   $qid =~ s/\D//g;

  my ($status) = $DB::dbh->selectrow_array( q{SELECT status FROM fragen WHERE frage_id = ?}, undef, $qid );
  my $kind  = Common::status_kind($status);
  my $dbg   = $Common::cgi->param('debug') ? "&debug=1" : "";
  my ($kapitel, $thema) = $DB::dbh->selectrow_array( q{SELECT kapitel, thema FROM session_quiz WHERE sessionid = ?}, undef, $Common::sid );

  my $ok = 'N';

  $DB::dbh->begin_work;

  if ($kind eq 'single' || $kind eq 'multi') {
    my $multi = ($kind eq 'multi') ? 1 : 0;
    my @selected = grep { defined && /^\d+$/ } $Common::cgi->param('aid');

    if (!$multi && @selected != 1) { $DB::dbh->rollback; Common::send_redirect(qs => "action=q&nr=$nr$dbg"); }
    if ($multi && @selected == 0)  { $DB::dbh->rollback; Common::send_redirect(qs => "action=q&nr=$nr$dbg"); }

    my $correct = $DB::dbh->selectcol_arrayref(q{ SELECT antwort_id FROM antworte WHERE frage_id = ? AND richtig = 'J' ORDER BY antwort_id }, undef, $qid);
    my @sel_sorted = sort { $a <=> $b } @selected;
    my @cor_sorted = sort { $a <=> $b } @$correct;

    if (!$multi) { my ($t) = $DB::dbh->selectrow_array( q{SELECT richtig FROM antworte WHERE antwort_id = ?}, undef, $sel_sorted[0] ); $ok = ($t && $t eq 'J') ? 'J' : 'N';  }
    else { if (@sel_sorted != @cor_sorted) { $ok = 'N'; } else { $ok = 'J'; for (my $i=0; $i<@sel_sorted; $i++) { if ($sel_sorted[$i] != $cor_sorted[$i]) { $ok = 'N'; last; } } } }

    if (!$multi) {
	$DB::dbh->do(q{ INSERT INTO geschichte(sessionid, kapitel, thema, frage, antwort, richtig) VALUES (?,?,?,?,?,?) },
			 undef, $Common::sid, $kapitel, $thema, $qid, $sel_sorted[0], $ok);
    } else {
      $DB::dbh->do(
        q{ INSERT INTO geschichte(sessionid, kapitel, thema, frage, antwort, richtig) VALUES (?,?,?,?,NULL,?) }, undef, $Common::sid, $kapitel, $thema, $qid, $ok
        );
      # Achtung: Spaltenname in DB evtl. 'frage' (nicht 'frage'). Wir lassen es wie im Bestand.
      $DB::dbh->do(q{DELETE FROM geschichte_wahl WHERE sessionid = ? AND frage = ?}, undef, $Common::sid, $qid);
      my $ins = $DB::dbh->prepare(q{ INSERT INTO geschichte_wahl(sessionid, frage, antwort_id) VALUES (?,?,?) });
      $ins->execute($Common::sid, $qid, $_) for @sel_sorted;
    }
  } elsif ($kind eq 'open') {
    my $user = $Common::cgi->param('user_text') // '';
    my $u = Common::norm_text($user);
    if ($u eq '') { $DB::dbh->rollback; Common::send_redirect(qs => "action=q&nr=$nr$dbg"); }

    my $rows = $DB::dbh->selectall_arrayref(q{ SELECT COALESCE(antwort_text, antwort) AS antwort, richtig FROM antworte WHERE frage_id = ? }, undef, $qid);

    my $hit = 0;
    for my $r (@$rows) { my ($a, $richtig) = @$r; next unless defined $a; if (Common::norm_text($a) eq $u) { $hit = 1; $ok = (defined $richtig && $richtig eq 'J') ? 'J' : 'N'; last; } }

    $ok = 'N' unless $hit;

    $DB::dbh->do(q{ INSERT INTO geschichte(sessionid, kapitel, thema, frage, antwort, richtig) VALUES (?,?,?,?,NULL,?) }, undef, $Common::sid, $kapitel, $thema, $qid, $ok);
    $DB::dbh->do(q{ INSERT INTO geschichte_text(sessionid, frage, typ, user_text) VALUES (?,?, 'O', ?) }, undef, $Common::sid, $qid, $user);
  }
  elsif ($kind eq 'formel') {
    my $latex = $Common::cgi->param('user_latex') // ''; my $mj_s  = $Common::cgi->param('user_mathjson') // '';
    if (($latex =~ /^\s*$/) && ($mj_s =~ /^\s*$/)) { $DB::dbh->rollback; Common::send_redirect(qs => "action=q&nr=$nr$dbg"); }
    # ???? 
    # if ( $mj_s !~ /^\s*$/ ) {
    #   my $rows = 
    #     $DB::dbh->selectall_arrayref( qq{SELECT richtig FROM antworte WHERE frage_id = ? AND antwort_mathjson = ?::jsonb}, undef, $qid, $mj_s );
    #   my $hitJ = 0; my $hitN = 0;
    #   for my $r (@$rows) { my ($richtig) = @$r; $hitJ = 1 if defined $richtig && $richtig eq 'J'; $hitN = 1 if !defined $richtig || $richtig ne 'J'; }
    #   $ok = $hitJ ? 'J' : 'N';
    # } else {
    #   # Fallback: LaTeX-String gegen akzeptierte Antworten
    #   my $u = Common::norm_text($latex);
    #   my $rows = $DB::dbh->selectall_arrayref(q{ SELECT COALESCE(antwort_latex, antwort) AS a, richtig FROM antworte WHERE frage_id = ? }, undef, $qid);
    #   my $hitJ = 0;
    #   for my $r (@$rows) { my ($a, $richtig) = @$r; next unless defined $a; if (Common::norm_text($a) eq $u) { $hitJ = 1 if defined $richtig && $richtig eq 'J'; } }
    #   $ok = $hitJ ? 'J' : 'N';
    # } # $mj_s !~ /^\s*$/

    my $ok = $Common::cgi->param('richtig') // 'N';

    $DB::dbh->do(q{INSERT INTO geschichte(sessionid, kapitel, thema, frage, antwort, richtig) VALUES (?,?,?,?,NULL,?) }, undef, $Common::sid, $kapitel, $thema, $qid, $ok);
    $DB::dbh->do(q{INSERT INTO geschichte_text(sessionid, frage, typ, user_latex, user_mathjson) VALUES (?,?, 'F', ?, NULLIF(?,'')::jsonb)}, undef, $Common::sid, $qid, $latex, $mj_s);

    # $DB::dbh->do(q{UPDATE antworte set antwort_latex=?, antwort_mathjson=NULLIF(?,'')::jsonb where frage_id=?}, undef, $latex, $mj_s,$qid);

  }  else { die "Unbekannter kind=$kind"; }

  $DB::dbh->commit;  
  
  my $answer = $Common::cgi->param('answer') // '0';
  Common::send_redirect(qs => "action=q&nr=" . ($nr+1) . $dbg."&answer=$answer");

} # save_answer - Ende

1;