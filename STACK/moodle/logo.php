<?php
// Rosette als Favicon, kompaktes Logo (Kopfzeile) und Logo (Anmeldeseite) in Moodle setzen
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
$ctx = context_system::instance(); $fs = get_file_storage();
foreach (["favicon" => "/tmp/rosette-6B-192.png", "logocompact" => "/tmp/rosette-6B-512.png", "logo" => "/tmp/rosette-6B-512.png"] as $area => $src) {
    $fs->delete_area_files($ctx->id, "core_admin", $area, 0);
    $name = "rosette-" . basename($src);
    $fs->create_file_from_pathname(["contextid" => $ctx->id, "component" => "core_admin", "filearea" => $area, "itemid" => 0,
        "filepath" => "/", "filename" => $name], $src);
    set_config($area, "/" . $name, "core_admin");
    echo "$area: /$name\n";
}
theme_reset_all_caches(); purge_all_caches();
