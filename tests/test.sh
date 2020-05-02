#!/bin/bash

shopt -s nullglob
failcount=0
passcount=0
for i in test_*; do
    # skip over html files
    [[ "$i" == *.html ]] && continue
    echo -ne "Testing $i..."
    python ../waveConstructor.py $i $i.html > /dev/null
    if ! diff $i.html ${i}_golden.html; then
        ((failcount++))
        echo "FAIL"
    else
        ((passcount++))
        echo "PASS"
        # automatically remove passing outputs
        rm $i.html
    fi
done
echo "Passed $passcount, failed $failcount, total $((passcount+failcount))"
