<?php
// Nur das Moodle-Favicon setzen (Logos bleiben): php fav_moodle.php /pfad/favicon.png
define("CLI_SCRIPT", true);
require("/srv/wwwservers/moodle/moodle/config.php");
$src = $argv[1]; $ctx = context_system::instance(); $fs = get_file_storage(); $name = basename($src);
$fs->delete_area_files($ctx->id, "core_admin", "favicon", 0);
$fs->create_file_from_pathname(["contextid" => $ctx->id, "component" => "core_admin", "filearea" => "favicon", "itemid" => 0, "filepath" => "/", "filename" => $name], $src);
set_config("favicon", "/" . $name, "core_admin"); theme_reset_all_caches(); echo "favicon: /$name\n";
