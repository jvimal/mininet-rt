#!/bin/sh

container=$1
lxc-execute -n "$container" \
  -s lxc.cgroup.cpuset.cpus=0 \
  -s  lxc.cgroup.cpu.cfs_quota_us=10000 \
  -s lxc.cgroup.cpu.cfs_period_us=20000 \
  /bin/bash

