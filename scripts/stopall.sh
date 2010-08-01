#!/bin/sh
n=`sudo vzlist -a -H | wc -l`
for i in `seq 1 $n`; do
  sudo vzctl stop $i &
done

