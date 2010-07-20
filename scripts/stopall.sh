#!/bin/sh

for i in `seq 1 10`; do
  sudo vzctl stop $i &
done

