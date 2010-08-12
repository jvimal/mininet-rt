import csv
import sys
sys.path = ['/home/jvimal/mininet'] + sys.path

from util import Command

# Worker threads
import eventlet
pool = eventlet.GreenPool(size = 50)

MEG = 10**6
exe='/home/jvimal/mininet/benchmark/cpu/cpu-stress'

def run_timer_test(t):
  """ Runs the test and returns the result """
  s = t/MEG
  us = t % MEG
  cmd = "%s %d %d" % (exe, s, us)
  c = Command(cmd)
  out = c.read_full().strip().split('\n')

  count = out[0]
  ask, got, latency = out[1].split(',')
  return {'timer' : t, 'count' : count, 'latency' : latency }


F = 10**4
timers = map(lambda x: F * x, range(1,10+1))

def timer_test(outfile):
  fields = ['timer','count','latency']
  f = open(outfile,'w')
  out = csv.DictWriter(f, fieldnames=fields)
  for t in timers:
    for i in xrange(0, 50):
      row = run_timer_test(t)
      print `row`
      out.writerow(row)
  f.close()

def timer_test_parallel(outfile):
  f = open(outfile,'w')
  fields = ['timer','count','latency']
  out = csv.DictWriter(f, fieldnames=fields)
  for t in timers:
    print 'Timer %d' % t
    f.flush()
    # spawn 50 timers
    lst = pool.imap(run_timer_test, [t]*50)
    out.writerows(lst)
 

outfile = 'test'
if len(sys.argv) > 1:
  outfile = sys.argv[1]

timer_test_parallel(outfile)

