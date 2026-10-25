#!/usr/bin/perl
# Weiterleitung von dispatch.cgi zum lokalen ilias (Kurs/Kategorie bwl-STACK)
use strict;
use warnings;
print "Status: 302 Found\r\nLocation: /ilias/goto.php?target=cat_87\r\n\r\n";
