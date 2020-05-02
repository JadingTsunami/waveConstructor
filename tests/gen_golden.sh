#!/bin/bash

shopt -s nullglob
total=0
for i in test_*; do
    # skip over html files
    [[ "$i" == *.html ]] && continue
    echo "Generating $i"
    python ../waveConstructor.py $i ${i}_golden.html > /dev/null
    ((total++))
done
echo "Generated $total golden outputs."

