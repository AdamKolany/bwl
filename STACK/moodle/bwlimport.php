<?php
// Kurs „Formeleditor in STACK“ anlegen, bwl-Fragen importieren, je Thema ein Test mit 3 Zufallsfragen.
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
require_once($CFG->dirroot . "/course/lib.php");
require_once($CFG->dirroot . "/question/format/xml/format.php");
require_once($CFG->libdir . "/questionlib.php");
require_once($CFG->libdir . "/testing/generator/lib.php");
require_once($CFG->dirroot . "/mod/quiz/locallib.php");
\core\session\manager::set_user(get_admin());
$course = $DB->get_record("course", ["shortname" => "bwl-STACK"]);
if (!$course) {
    $course = create_course((object)["fullname" => "Formeleditor in STACK (bwl-Aufgabenauswahl)", "shortname" => "bwl-STACK",
        "category" => 1, "summary" => "Machbarkeitstest: bwl-Formeleditor als Eingabe für STACK-Fragen.", "format" => "topics", "numsections" => 1]);
}
$ctx = context_course::instance($course->id);
$top = question_get_top_category($ctx->id, true);
$q = new qformat_xml(); $q->setCategory(question_make_default_categories([$ctx])); $q->setContexts([$ctx]);
$q->setCourse($course); $q->setFilename(($argv[1] ?? "/tmp/bwl-stack.xml")); $q->setRealfilename("bwl-stack.xml");
$q->setMatchgrades("error"); $q->setCatfromfile(true); $q->setContextfromfile(false); $q->setStoponerror(true);
$q->displayprogress = false;
$ok = true; if ($DB->count_records_select("question_categories", "contextid = ? AND name = ?", [$ctx->id, "Ableitungen"]) == 0) { ob_start(); $ok = $q->importpreprocess() && $q->importprocess() && $q->importpostprocess(); $log = ob_get_clean(); } else { $log = "(schon importiert)"; }
echo $ok ? "Import OK\n" : "Import FEHLER\n" . strip_tags($log) . "\n";
$gen = new testing_data_generator();
foreach ($DB->get_records_select("question_categories", "contextid = ? AND parent <> 0 AND name <> ?", [$ctx->id, "bwl-Aufgabenauswahl"], "name") as $cat) {
    if ($cat->parent == $top->id) continue;                        // nur die Themen-Unterkategorien
    foreach ($DB->get_records("quiz", ["course" => $course->id, "name" => $cat->name]) as $old) {   // halbfertige Tests weg
        course_delete_module(get_coursemodule_from_instance("quiz", $old->id)->id);
    }
    $quiz = $gen->create_module("quiz", ["course" => $course->id, "name" => $cat->name, "section" => 1, "questionsperpage" => 1,
        "preferredbehaviour" => "interactive", "grade" => 3, "sumgrades" => 0]);
    $structure = \mod_quiz\quiz_settings::create($quiz->id)->get_structure();
    $filter = ["category" => ["jointype" => \core_question\local\bank\condition::JOINTYPE_DEFAULT,
        "values" => [$cat->id], "filteroptions" => ["includesubcategories" => false]]];
    $structure->add_random_questions(0, 3, ["filter" => $filter]);
    quiz_update_sumgrades(\mod_quiz\quiz_settings::create($quiz->id)->get_quiz());
    echo "Test: {$cat->name} (", $DB->count_records("question_bank_entries", ["questioncategoryid" => $cat->id]), " Fragen)\n";
}
echo "Kurs-ID {$course->id}\n";
