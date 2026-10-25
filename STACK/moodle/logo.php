<?php
// Logo (Anmeldeseite) und kompaktes Logo (Kopfzeile) in Moodle setzen: php logo.php /pfad/bild.png
// (Favicon separat: fav_moodle.php). Aktuell: Penrose-Dreieck ptr1-512.png; vorher Rosette 6B.
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
$src = $argv[1]; $ctx = context_system::instance(); $fs = get_file_storage(); $name = basename($src);
foreach (["logocompact", "logo"] as $area) {
    $fs->delete_area_files($ctx->id, "core_admin", $area, 0);
    $fs->create_file_from_pathname(["contextid" => $ctx->id, "component" => "core_admin", "filearea" => $area, "itemid" => 0,
        "filepath" => "/", "filename" => $name], $src);
    set_config($area, "/" . $name, "core_admin");
    echo "$area: /$name\n";
}
theme_reset_all_caches(); purge_all_caches();
