#!/bin/bash
# Editor-Seite bauen und veröffentlichen. vorlage.html = eine echte bwl-Fragenseite (doit.cgi), wird bei Bedarf geholt.
# Ziel: /stackbwl/ auf dem Hauptserver (Port 80); STACK-Fragen binden …/stackbwl/editor.html ein.
set -e
D=$(cd "$(dirname "$0")" && pwd); ZIEL=${ZIEL:-/srv/wwwservers/www/main/html/stackbwl}
if [ ! -f vorlage.html ]; then
  B=${BWL:-http://mathe-c10-mua.inw.hs-merseburg.de/cgi-bin/teste/bwl/doit.cgi}; J=$(mktemp)
  curl -s -c "$J" -b "$J" "$B?action=menu&kapitel=TSTA&thema=abltn" >/dev/null
  curl -s -L -c "$J" -b "$J" "$B?action=start&kapitel=TSTA&thema=abltn&n=1" > vorlage.html; rm -f "$J"
fi
mkdir -p "$ZIEL"
python3 "$D/mkeditor.py" vorlage.html "$ZIEL/editor.html"
cp "$D/bridge.js" "$D/mj2max.js" "$D/max2tex.js" "$ZIEL/"
echo "→ $ZIEL"
