#!/bin/bash
# Zip the deliverables in two halves (upload limit 30 MB): docx/pdf/md per lecture, the figures the .md files reference.
set -e
cd "$(dirname "$0")/.."
rm -f outputs/Shastrarth_Prakaran_Lectures*_EN.zip
for half in "01-06:01 02 03 04 05 06" "07-12:07 08 09 10 11 12"; do
  range=${half%%:*}; nums=${half#*:}
  stage=/tmp/vv_pkg_$range/Shastrarth_Prakaran_EN_Lectures$range
  rm -rf /tmp/vv_pkg_$range && mkdir -p "$stage"
  for n in $nums; do
    cp outputs/Shastrarth_Prakaran_Lecture${n}_*EN.* "$stage"/
    cp -r build/figs$n "$stage"/
  done
  cp outputs/Shastrarth_Prakaran_Closing_Reports.md outputs/Shastrarth_Prakaran_Appendix_Karikas_Prakasha_1943.* "$stage"/
  (cd /tmp/vv_pkg_$range && zip -qr - "$(basename "$stage")") > outputs/Shastrarth_Prakaran_Lectures${range}_EN.zip
done
ls -la outputs/*.zip
