#!/bin/bash
# v03_02: Intro (Penrose → Rosette → Titel) + Blasen mit Hand-Umbrüchen + Legende höher + langsame Rosetten-Endkarte
#         + neue Stimme (XTTS: Melodie von Thorsten, Klangfarbe Adam), Ton nachbearbeitet
set -e
F=$(ls -d /home/adamkolany/*Claude*Codex*/MuA/mathe-C10/Filme); Q="$F/_Quellen"
B=$(ls -d "$F"/Tastatur-Schulung*03_02*Blasen.txt); V0=$(ls -d "$F"/Tastatur-Schulung*03_00.mp4)
OFF=12.5   # Inhalt beginnt nach dem Intro (13,5 s, davon 1 s Überblendung)
cd /tmp/mb3
[ -n "$SKIPBUB" ] || python3 bubbles3b.py render /tmp/mb3/bub3b.mp4 "$B"
ffmpeg -v error -y -i bub3b.mp4 -vf "select=eq(n\,9670)" -frames:v 1 lastcontent.png
cp "$Q/ros6_hi.png" "$Q/Ende.png" "$Q/endcard.py" .
python3 endcard.py lastcontent.png | ffmpeg -v error -y -f rawvideo -pix_fmt bgr24 -s 1920x1200 -r 30 -i - -c:v libx264 -crf 18 -pix_fmt yuv420p endcard.mp4
"$(ls -d /home/adamkolany/*Claude*Codex*/System/Szeptucha)/venv/bin/python" vo4/mix2.py vo4 v3take.srt vo4/voice_raw.wav | tee vo4/mix.log
ffmpeg -v error -y -i vo4/voice_raw.wav -af "highpass=f=70,adeclick,afftdn=nr=12:nf=-45,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-18:TP=-1.5,adelay=${OFF/./}00|0" -ar 48000 vo4/voice.wav
ffmpeg -v error -y -i intro.mp4 -i bub3b.mp4 -i endcard.mp4 -i vo4/voice.wav -filter_complex \
  "[1:v]trim=end_frame=9671,setpts=PTS-STARTPTS[c];[0:v][c]xfade=transition=fade:duration=1:offset=$OFF[ic];[2:v]setpts=PTS-STARTPTS[e];[ic][e]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -map 3:a -af apad -c:v libx264 -crf 20 -preset medium -r 30 -c:a aac -b:a 128k -shortest -movflags +faststart v0302.mp4
O="${V0/03_00/03_02}"; cp v0302.mp4 "$O"
python3 mksrt.py v3take.srt "$B" $OFF "${O%.mp4} -- Untertitel.srt"
cp vo4/lines.txt "${O%.mp4} -- Sprechtext.txt"
cp bubbles3b.py build0302.sh mksrt.py vo4/mix2.py vo4/hybrid.py "$Q/"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$O"; ls -l "$F" | grep 03_02
