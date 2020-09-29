#!/usr/bin/env bash
set -euo pipefail
if test -f content.tex; then
    mv content.tex content.tex.bac_$(date "+%Y-%m-%d-%H:%M:%S")
fi
python getcontent.py;
latexmk -f main.tex;
mv main.pdf journals-$(date "+%Y-%m-%d");
if test -f content.tex; then
    mv content.tex content-$(date "+%Y-%m-%d").tex
fi
