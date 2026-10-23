<?php
// Kurs anlegen (falls nötig), STACK-Fragen aus XML importieren, für jede neue Themen-Kategorie einen Test mit 3 Zufallsfragen.
// Aufruf: sudo -u www-data php kurs.php <kurzname> "<voller Name>" <pfad/zu/fragen.xml> [lehrende] [teilnehmende]
// Beispiel: php kurs.php bwl-STACK-alt "Testmaterial (alt): henning, julia" /tmp/bwl-stack-alle.xml mua stacktest
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
require_once($CFG->dirroot . "/course/lib.php");
require_once($CFG->dirroot . "/question/format/xml/format.php");
require_once($CFG->libdir . "/questionlib.php");
require_once($CFG->libdir . "/testing/generator/lib.php");
require_once($CFG->libdir . "/enrollib.php");
require_once($CFG->dirroot . "/mod/quiz/locallib.php");
[$short, $full, $xml] = [$argv[1], $argv[2], $argv[3]];
$teacher = $argv[4] ?? "mua"; $student = $argv[5] ?? "stacktest";
\core\session\manager::set_user(get_admin());
$course = $DB->get_record("course", ["shortname" => $short]);
if (!$course) {
    $course = create_course((object)["fullname" => $full, "shortname" => $short, "category" => 1, "format" => "topics", "numsections" => 1,
        "summary" => "bwl-Formeleditor in STACK-Fragen."]);
}
$ctx = context_course::instance($course->id);
$before = $DB->get_fieldset_select("question_categories", "id", "contextid = ?", [$ctx->id]);
$q = new qformat_xml(); $q->setCategory(question_make_default_categories([$ctx])); $q->setContexts([$ctx]);
$q->setCourse($course); $q->setFilename($xml); $q->setRealfilename(basename($xml));
$q->setMatchgrades("error"); $q->setCatfromfile(true); $q->setContextfromfile(false); $q->setStoponerror(true); $q->displayprogress = false;
ob_start(); $ok = $q->importpreprocess() && $q->importprocess() && $q->importpostprocess(); $log = ob_get_clean();
echo $ok ? "Import OK\n" : "Import FEHLER\n" . strip_tags($log) . "\n";
// Tests nur für neu entstandene Blatt-Kategorien (mit Fragen)
$gen = new testing_data_generator();
$cats = $DB->get_records_select("question_categories", "contextid = ?", [$ctx->id], "name");
foreach ($cats as $cat) {
    if (in_array($cat->id, $before)) continue;
    $n = $DB->count_records("question_bank_entries", ["questioncategoryid" => $cat->id]);
    if ($n == 0) continue;
    $quiz = $gen->create_module("quiz", ["course" => $course->id, "name" => $cat->name, "section" => 1, "questionsperpage" => 1,
        "preferredbehaviour" => "interactive", "grade" => min(3, $n), "sumgrades" => 0]);
    $filter = ["category" => ["jointype" => \core_question\local\bank\condition::JOINTYPE_DEFAULT,
        "values" => [$cat->id], "filteroptions" => ["includesubcategories" => false]]];
    \mod_quiz\quiz_settings::create($quiz->id)->get_structure()->add_random_questions(0, min(3, $n), ["filter" => $filter]);
    quiz_update_sumgrades(\mod_quiz\quiz_settings::create($quiz->id)->get_quiz());
    echo "Test: {$cat->name} ($n Fragen)\n";
}
$plugin = enrol_get_plugin("manual"); $inst = $DB->get_record("enrol", ["courseid" => $course->id, "enrol" => "manual"]);
foreach ([[$teacher, "editingteacher"], [$student, "student"]] as [$un, $role]) {
    if ($u = $DB->get_record("user", ["username" => $un])) $plugin->enrol_user($inst, $u->id, $DB->get_field("role", "id", ["shortname" => $role]));
}
echo "Kurs-ID {$course->id}\n";
