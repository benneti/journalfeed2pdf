#!/usr/bin/env bash
set -euo pipefail

if [ -z ${1+x} ]; then
    fname=journalfeed-$(date "+%Y-%m-%d").pdf
else
    if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        echo "Usage: bash "$0" <output.pdf>"
        echo "or:    bash "$0
        echo "The latter will output to journalfeed-"$(date "+%Y-%m-%d")".pdf"
        exit
    fi
    fname=$1
fi

# variables for the relevant directories
temp_dir=$(mktemp -d -t journalfeed.XXXXXX)
script_dir=$(dirname -- "$0")
pwd_dir=$(pwd)

# get the content and move it to the temp compile directory
python3 $script_dir/getcontent.py $temp_dir/content.tex
cp $script_dir/main.tex $temp_dir/main.tex
# cd and create pdf
cd $temp_dir
latexmk -f main.tex
cd $pwd_dir
mv $temp_dir/main.pdf $fname
