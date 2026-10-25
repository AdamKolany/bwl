#!/usr/bin/perl
# Weiterleitung von dispatch.cgi zum lokalen moodle (Kurs/Kategorie bwl-STACK)
use strict;
use warnings;
print "Status: 302 Found\r\nLocation: /moodle/course/view.php?id=2\r\n\r\n";
