#!/bin/sh
# this isn't straightforward, but hey
# who's spawning more than 254 hosts?

DEV=veth1.0
#CT_IP1=`ifconfig $DEV | egrep 'inet' | cut -d ' ' -f 12 | cut -d ':' -f 2`
#echo $DEV $CT_IP1
#exit 0
#
tc qdisc del dev $DEV root
tc qdisc add dev $DEV root handle 1:0 htb default 10 # default class 10

for i in `seq 1 10`; do
  tc class add dev $DEV parent 1:0 classid 1:$i htb rate 100mbit burst 15k
  tc filter add dev $DEV protocol ip \
    parent 1:0 prio 1 \
    u32 match ip src 10.0.0.$i flowid 1:$i
done

exit 0
