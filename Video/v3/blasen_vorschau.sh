#!/bin/bash
# Schnelle Vorschau nur der Blasen (mit Ton) aus dem aktuellen Blasen.txt, ~1 Min.
set -e
F=$(ls -d /home/adamkolany/*Claude*Codex*/MuA/mathe-C10/Filme)
B=$(ls -d "$F"/Tastatur-Schulung*03_02*Blasen.txt); V0=$(ls -d "$F"/Tastatur-Schulung*03_00.mp4)
O="$F/Tastatur-Schulung, v 03_02 -- Blasen-Vorschau.mp4"; O="${O// /$' '}"
# erst in eine Temp-Datei, dann verschieben – sonst sieht der Player eine halbfertige Datei
cd /tmp/mb3 && python3 bubbles3b.py blasen /tmp/mb3/vorschau.mp4 "$B" "$V0" && mv -f /tmp/mb3/vorschau.mp4 "$O"
