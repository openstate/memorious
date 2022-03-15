#!/bin/sh
cd /memorious
#memorious run covid19
cd /data/results/covid19
for i in *.json; do
  fn=`basename $i .json`
  if [ ! -d "$fn" -a -s "$fn.data.pdf" ]; then
    echo "Should make directory $fn now"
    mkdir -p $fn
    cd $fn
    pdfseparate "../$fn.data.pdf" "$fn-%05d.pdf"
    cd ..
  fi
done
