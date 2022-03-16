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
    pdfseparate "../$fn.data.pdf" "Pagina %05d.pdf"
    cd ..
  fi
done
python3 load_covid19.py -f $COVID19_ALEPH_FOREIGN_ID -d /data/results/covid19/ -b 0
rm -fr /data/results/covid19/*
