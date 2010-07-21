
from net import Mininet
from node import Host, Switch
from topo import SingleSwitchTopo, LinearTopo
from tests import IPerfOneToAllTest, CPUStressTest

import html
import sys
from time import sleep
import getopt

from settings import n, t, rate, outputfile, detach, dryrun
from help import printhelp

def main():
  # number of hosts
  n = 10

  # time to run, parameter to iperf
  t = 10

  # rate limit interfaces?
  rate = None

  # where to store output of experiments
  outputfile = ''

  # should we detach from terminal after booting host?
  detach = False

  # Just check the commands that will be executed
  dryrun = False

  optlist, args = getopt.getopt(sys.argv[1:], 'n:t:r:o:dph')
  for (o,a) in optlist:
    if o == '-n':
      n = int(a)
    if o == '-t':
      t = int(a)
    if o == '-r':
      rate = a
    if o == '-o':
      outputfile = a
    if o == '-d':
      detach = True
    if o == '-p':
      dryrun = True
    if o == '-h':
      printhelp()
      sys.exit(0)

  if outputfile == '':
    outputfile = 'results-%d-%d.html' % (n, t)
  
  topo = LinearTopo(n)
  m = Mininet(HostClass=Host, SwitchClass=Switch, topo=topo, rate=rate)
  
  m.start()
  
  it = IPerfOneToAllTest(m.hosts, t)
  it.start()

  if detach:
    return

  if not dryrun:
    while True:
      x = int(raw_input())
      if x == 1:
        break

  res = it.end()

  html.html(outputfile, html.comments([
    'topology:' + '%s' % (topo),
  ]) + res)

  m.stop()
  #m.destroy()

main()

