#!/bin/sh

container=$1
quota=$2
period=$3

lxc-execute -n "$container" \
  -s lxc.cgroup.cpuset.cpus=0 \
  -s  lxc.cgroup.cpu.cfs_quota_us=$quota \
  -s lxc.cgroup.cpu.cfs_period_us=$period \
  ./cpu-stress 10 0
  #python timer_latency.py $quota-$period
  #./steal_cpu 500000

