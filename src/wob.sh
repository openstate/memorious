#!/bin/sh
cd /memorious
memorious run wob
RESULTSDIR=$1
if [ -e "$1" ]; then
  RESULTSDIR=/data/results/wob
fi
FID=$2
if [ -e "$2" ]; then
  FID=$COVID19_ALEPH_FOREIGN_ID
fi
echo "Uploading to alepg $FID from $RESULTSDIR"
cd $RESULTSDIR
for i in *.json; do
  fn=`basename $i .json`
  echo $fn
  echo "----------"
  for j in $fn.*.pdf; do
    fn2=`basename $j .pdf`
    fn3=`echo -n $fn2 |awk 'BEGIN{FS="."}{printf("%s",$1);}'`
    echo "$fn2 => $fn3"
    if [ ! -d "$fn3" -a -s "$fn2.pdf" ]; then
      echo "Should make directory $fn3 now"
      mkdir -p $fn3
      cd $fn3
      pdfseparate "../$fn2.pdf" "Pagina %05d.pdf"
      cd ..
    fi
  done
  echo "----------"
done
cd /crawlers/src
python3 load_covid19.py -f $FID  -d $RESULTSDIR -b 10 -s 10
#rm -fr /data/results/covid19/*
