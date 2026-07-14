package reset_session;

use CGI qw(:standard escapeHTML);
use utf8;
use strict;

require './Modules/Common.pm';
require './Modules/DB.pm';

# ============================================================
# MENÜ
# ============================================================
sub run {
  if ($Common::sid) {
    $DB::dbh->do(q{DELETE FROM session_quiz WHERE sessionid = ?}, undef, $Common::sid);
    $DB::dbh->do(q{DELETE FROM session_questions WHERE sessionid = ?}, undef, $Common::sid);
    $DB::dbh->do(q{DELETE FROM geschichte WHERE sessionid = ?}, undef, $Common::sid);
  }
  Common::send_redirect(qs => "action=menu" . ($Common::cgi->param('debug') ? "&debug=1" : ""));
} # reset_session - Ende

1;