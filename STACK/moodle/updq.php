<?php
// Fragetext, Musterlösung (Fragevariablen) und allgemeines Feedback vorhandener Fragen aus neu erzeugter XML übernehmen (statt neu importieren)
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
$x = simplexml_load_file(($argv[1] ?? "/tmp/bwl-stack.xml")); $n = 0;
foreach ($x->question as $q) {
    if ((string)$q["type"] !== "stack") continue;
    $idn = (string)$q->idnumber; $text = (string)$q->questiontext->text;
    $qids = $DB->get_fieldset_sql("SELECT qv.questionid FROM {question_bank_entries} qbe JOIN {question_versions} qv ON qv.questionbankentryid = qbe.id WHERE qbe.idnumber = ?", [$idn]);
    foreach ($qids as $qid) { $DB->set_field("question", "questiontext", $text, ["id" => $qid]); $DB->set_field("question", "generalfeedback", (string)$q->generalfeedback->text, ["id" => $qid]); $DB->set_field("qtype_stack_options", "questionvariables", (string)$q->questionvariables->text, ["questionid" => $qid]); $DB->set_field("qtype_stack_options", "compiledcache", null, ["questionid" => $qid]); $n++; }
}
purge_all_caches(); echo "aktualisiert: $n\n";
