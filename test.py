
from net import Mininet
from node import Host, Switch
from topo import SingleSwitchTopo, LinearTopo
from tests import IPerfOneToAllTest, CPUStressTest

import html
import sys
from time import sleep
import getopt

import settings as s
from help import printhelp

def main():
  # number of hosts
  s.n = 10

  # time to run, parameter to iperf
  s.t = 10

  # rate limit interfaces?
  s.rate = None

  # where to store output of experiments
  s.outputfile = ''

  # should we detach from terminal after booting host?
  s.detach = False

  # Just check the commands that will be executed
  s.dryrun = False
  
  s.test = ''

  optlist, args = getopt.getopt(sys.argv[1:], 'n:t:r:o:dphT:s')
  for (o,a) in optlist:
    if o == '-n':
      s.n = int(a)
    if o == '-t':
      s.t = int(a)
    if o == '-r':
      s.rate = a
    if o == '-o':
      s.outputfile = a
    if o == '-d':
      s.detach = True
    if o == '-p':
      s.dryrun = True
    if o == '-h':
      printhelp()
      sys.exit(0)
    if o == '-T':
      s.test = a
    if o == '-s':
      s.stop = True

  if s.outputfile == '':
    s.outputfile = 'results-%d-%d.html' % (s.n, s.t)
  
  topo = LinearTopo(s.n)
  m = Mininet(HostClass=Host, SwitchClass=Switch, topo=topo, rate=s.rate)
  m.start()

  if s.stop:
    m.stop()
    return
  
  if s.test == 'iperf':
    it = IPerfOneToAllTest(m.hosts, s.t)
    it.start()

  if s.detach:
    return

  if not s.dryrun:
    while True:
      x = int(raw_input())
      if x == 1:
        break

    res = it.end()
  
    html.html(s.outputfile, html.comments([
      'topology:' + '%s' % (topo),
    ]) + res)

  m.stop()
  #m.destroy()

main()

