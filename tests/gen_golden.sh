#!/bin/bash

shopt -s nullglob
total=0
for i in *[^.html]; do
    echo "Generating $i"
    python ../waveConstructor.py $i ${i}_golden.html > /dev/null
    ((total++))
done
echo "Generated $total golden outputs."

