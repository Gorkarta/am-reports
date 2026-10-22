#!/usr/bin/env bash
# Пересборка оболочек дашбордов (Портфель, Каналы, Анализ продажи билетов) из репозитория — без внешних файлов.
# Использование:  bash rebuild_shells.sh [папка_вывода]   (по умолчанию ./shells)
# Данные для встроенного снимка берутся из dashboards/data/ (последний расчёт workflow).
set -euo pipefail
cd "$(dirname "$0")/src"
OUT="${1:-../shells}"; mkdir -p "$OUT"
M="../masters"
python3 -s mk_shell.py ../data/pf_page.json ../data/channels.json "$M/Каналы продаж — портфельная аналитика (мастер, до оболочки).html" "$OUT"
python3 -s mk_shell_d3.py ../data/events.json "$M/Анализ продажи билетов (мастер, до оболочки).html" "$OUT/Анализ продажи билетов.html"
echo "Готово: $OUT"
