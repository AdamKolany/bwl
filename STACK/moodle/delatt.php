<?php define("CLI_SCRIPT", true); require("/srv/wwwservers/moodle/moodle/config.php"); require_once($CFG->dirroot . "/mod/quiz/locallib.php");
$u = $DB->get_record("user", ["username" => "stacktest"]); $n = 0;
foreach ($DB->get_records("quiz_attempts", ["userid" => $u->id]) as $a) { quiz_delete_attempt($a, $DB->get_record("quiz", ["id" => $a->quiz])); $n++; }
echo "gelöscht: $n\n";
