<?php
// Tests eines Kurses neu aufbauen: je Themen-Kategorie (mit Fragen) ein Test mit N Zufallsfragen (Standard 5).
// Vorhandene Tests des Kurses werden gelöscht (samt Versuchen). Aufruf: sudo -u www-data php tests.php <kurzname> [N]
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
require_once($CFG->dirroot . "/course/lib.php");
require_once($CFG->libdir . "/testing/generator/lib.php");
require_once($CFG->dirroot . "/mod/quiz/locallib.php");
$short = $argv[1]; $N = (int)($argv[2] ?? 5);
\core\session\manager::set_user(get_admin());
$course = $DB->get_record("course", ["shortname" => $short], "*", MUST_EXIST);
$ctx = context_course::instance($course->id);
foreach ($DB->get_records("quiz", ["course" => $course->id]) as $old) {
    course_delete_module(get_coursemodule_from_instance("quiz", $old->id)->id);
}
$gen = new testing_data_generator();
foreach ($DB->get_records_select("question_categories", "contextid = ?", [$ctx->id], "name") as $cat) {
    $n = $DB->count_records("question_bank_entries", ["questioncategoryid" => $cat->id]);
    if ($n == 0) continue;
    $k = min($N, $n);
    $quiz = $gen->create_module("quiz", ["course" => $course->id, "name" => $cat->name, "section" => 1, "questionsperpage" => 1,
        "preferredbehaviour" => "interactive", "grade" => $k, "sumgrades" => 0]);
    $filter = ["category" => ["jointype" => \core_question\local\bank\condition::JOINTYPE_DEFAULT,
        "values" => [$cat->id], "filteroptions" => ["includesubcategories" => false]]];
    \mod_quiz\quiz_settings::create($quiz->id)->get_structure()->add_random_questions(0, $k, ["filter" => $filter]);
    quiz_update_sumgrades(\mod_quiz\quiz_settings::create($quiz->id)->get_quiz());
    echo "Test: {$cat->name} ($k von $n)\n";
}
