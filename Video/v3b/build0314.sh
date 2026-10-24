#!/bin/bash
# v03_14: wie v03_13, Rosette in Intro und Endkarte zyklisch geflochten (letzte Kopie unter der ersten, draw_woven)
# v03_13: wie v03_12, aber auch das Intro mit 8 Armen (Intro-Escher-A2-n8.mp4, ROSETTE_N=8)
# v03_12: wie v03_11 (Ton mit „gerutscht“-Korrektur), neue Endkarte: Rosette mit 8 Armen entsteht wie im Intro aus dem
#         Dreieck, Seitenhintergrund verlischt, Ente wächst als Ellipse → Rechteck (weich überblendet), dann Schwarz (endcard5.py)
# v03_10: wie v03_09, Escher-Dreieck mit dickeren Balken (escher-Drehpunkt-A, v 01_01.svg, b=0.55), Endkarte wie v03_08 (Geist), Ente bildschirmfüllend, dann Ausblenden nach Schwarz
# v03_09: wie v03_08, Endkarte (Ente) fast bildschirmfüllend: 95 % Höhe, 20 % breiter gestreckt, weißer Hintergrund
# v03_08: wie v03_07, aber Intro und Endrosette aus escher-Drehpunkt-A, v 01_01.svg (Adams Escher-Dreieck)
# v03_07: wie v03_06 (gleiche Aufnahme), dazu Owal um die Zielformel bei „Die Aufgabe: …“
# v03_06: Aufnahme v6take (record6.py): Zielformel vor dem Satz da, ⇧ alle Zustände im Zähler des 2. Bruchs,
#         ← → bis in den Exponenten unter der Wurzel, „heraus“ ×3, e^{−x/2} mit □^{□/□}, ohne „Los geht’s“;
#         Endkarte: nach der Rosette kürzer und mit Beschleunigung (endcard.py hier in /tmp/mb4).
set -e
F=$(ls -d /home/adamkolany/*Claude*Codex*/MuA/mathe-C10/Filme); Q="$F/_Quellen"
B0=$(ls -d "$F"/Tastatur-Schulung*03_13*Blasen.txt); V0=$(ls -d "$F"/Tastatur-Schulung*03_00.mp4)
O="${V0/03_00/03_14}"; B="${O%.mp4} -- Blasen.txt"
OFF=12.5; M=/tmp/mb3
[ -f "$Q/Intro-Escher-A2-n8.mp4" ] || ROSETTE_N=8 PENROSE_SVG="$Q/escher-Drehpunkt-A, v 01_01.svg" OUT=Intro-Escher-A2-n8 "$Q/intro_vorschau.sh" 2>&1 | grep -v WARN
export Q; PENROSE_SVG="$Q/escher-Drehpunkt-A, v 01_01.svg" python3 /tmp/mb4/mkros.py /tmp/mb4/ros_escherA2.png
cd /tmp/mb4
export SS=$(python3 sync.py v6take.mp4); echo "SS=$SS"
[ -f "$B" ] || cp "$B0" "$B"
python3 field6.py | tail -1
[ -n "$SKIPBUB" ] || TAKE=v6take SRT=/tmp/mb4/v6take2.srt python3 bubbles6.py render /tmp/mb4/bub6.mp4 "$B"
NF=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 bub6.mp4); LAST=$((NF - 24))
ffmpeg -v error -y -i bub6.mp4 -vf "select=eq(n\,$LAST)" -frames:v 1 lastcontent.png
cp $M/Ende.png .
ROSETTE_N=8 PENROSE_SVG="$Q/escher-Drehpunkt-A, v 01_01.svg" python3 endcard5.py lastcontent.png | ffmpeg -v error -y -f rawvideo -pix_fmt bgr24 -s 1920x1200 -r 30 -i - -c:v libx264 -crf 18 -pix_fmt yuv420p endcard.mp4
"$(ls -d /home/adamkolany/*Claude*Codex*/System/Szeptucha)/venv/bin/python" $M/vo4/mix2.py vo6 v6take2.srt vo6/voice_raw.wav | tee vo6/mix.log
ffmpeg -v error -y -i vo6/voice_raw.wav -af "highpass=f=70,adeclick,afftdn=nr=12:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-18:TP=-1.5,adelay=${OFF/./}00|0" -ar 48000 vo6/voice.wav
VEND=$(tail -1 vo6/mix.log | awk '{print $7}'); HOLD=$(python3 -c "print(max(0, round($VEND + 1.2 - ($LAST + 1) / 30, 2)))"); echo "Standbild $HOLD s"
ffmpeg -v error -y -i "$Q/Intro-Escher-A2-n8.mp4" -i bub6.mp4 -i endcard.mp4 -i vo6/voice.wav -filter_complex \
  "[1:v]trim=end_frame=$((LAST + 1)),setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=$HOLD[c];[0:v][c]xfade=transition=fade:duration=1:offset=$OFF[ic];[2:v]setpts=PTS-STARTPTS[e];[ic][e]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -map 3:a -af apad -c:v libx264 -crf 20 -preset medium -r 30 -c:a aac -b:a 128k -shortest -movflags +faststart v0314.mp4
cp v0314.mp4 "$O"
python3 $M/mksrt.py v6take2.srt "$B" $OFF "${O%.mp4} -- Untertitel.srt"
cp vo6/lines.txt "${O%.mp4} -- Sprechtext.txt"
cp record6.py bubbles6.py bubble.py build0314.sh endcard5.py mkros.py field6.py sync.py mk0306.py endcard.py v6take2.srt "$Q/"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$O"; ls -l "$F" | grep -a 03_14 || true
