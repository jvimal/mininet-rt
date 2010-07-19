
from net import Mininet
from node import Host, Switch
from topo import SingleSwitchTopo, LinearTopo
from tests import IPerfOneToAllTest, CPUStressTest

import html
import sys
from time import sleep
import getopt

def main():
  n = 10
  t = 10

  optlist, args = getopt.getopt(sys.argv[1:], 'n:t:')
  for (o,a) in optlist:
    if o == '-n':
      n = int(a)
    if o == '-t':
      t = int(a)

  outputfile = 'results-%d-%d.html' % (n, t)
  
  topo = LinearTopo(n)
  m = Mininet(HostClass=Host, SwitchClass=Switch, topo=topo)
  
  m.start()
  
  it = IPerfOneToAllTest(m.hosts, t)
  it.start()
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

