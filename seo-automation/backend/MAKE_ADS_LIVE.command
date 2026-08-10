#!/bin/bash
cd "$(dirname "$0")"
echo "============================================"
echo " ZeOrbit — Make Google Ads LIVE"
echo "============================================"
echo ""
echo "1) A browser will open."
echo "2) Sign in with the Google Ads owner account."
echo "3) Click Allow."
echo "4) Wait for SUCCESS in this window."
echo ""
read -p "Press Enter to start..."
lsof -tiTCP:8080 -sTCP:LISTEN | xargs kill -9 2>/dev/null
python3 scripts/complete_oauth_ads.py
echo ""
echo "Restarting API..."
lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill -9 2>/dev/null
sleep 1
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
sleep 3
echo ""
echo "Status:"
curl -s http://127.0.0.1:8000/api/google-ads/status
echo ""
echo ""
read -p "Done. Press Enter to close."
