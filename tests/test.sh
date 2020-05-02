#!/bin/bash

shopt -s nullglob
failcount=0
passcount=0
for i in *[^.html]; do
    echo -ne "Testing $i..."
    python ../waveConstructor.py $i $i.html > /dev/null
    if ! diff $i.html ${i}_golden.html; then
        ((failcount++))
        echo "FAIL"
    else
        ((passcount++))
        echo "PASS"
    fi
done
echo "Passed $passcount, failed $failcount, total $((passcount+failcount))"
read -p "Clean outputs? [yN]" -t 2 choice
if [[ -n "$choice" && "$choice" =~ [yY] ]]; then
    for i in *[^.html]; do
        rm $i.html
        echo "Removed $i.html"
    done
fi
