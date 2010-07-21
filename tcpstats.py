#!/bin/env python

# collects tcp statistics; collects
# only txqueue length (i.e., window size in bytes?)

import sys
from time import sleep

file = '/proc/net/tcp'
t = 0

def collect():
  lines = map(lambda s: s.strip().split(' '), open(file,'r').readlines())
  txqueue_len = -1
  for l in lines:
    if l[2] == '0100000A:1389':
      txqueue_len = int(l[4].split(':')[0], 16)
  return txqueue_len

print 'Time,TxQueueLength'
while 1:
  l = collect()
  if l != -1:
    print "%d,%d" % (t, collect())
    sys.stdout.flush()
    t += 1
  sleep(1)

