#!/bin/sh

cpu="$1"
echo $cpu
for i in `seq 1 10`; do
  sudo vzctl set $i --cpuunits $cpu --save
done

