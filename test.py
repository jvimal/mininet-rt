
from net import Mininet
from node import Host, Switch
from topo import SingleSwitchTopo
from tests import IPerfOneToAllTest

import html
import sys
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

  topo = SingleSwitchTopo(n)
  m = Mininet(HostClass=Host, SwitchClass=Switch, topo=topo)
  
  m.start()
  it = IPerfOneToAllTest(m.hosts, t)
  it.start()
  res = it.end()

  html.html(outputfile, html.comments([
    'topology:' + 'LinearTopo(%d)' % n,
  ]) + res)

  m.stop()
  #m.destroy()

main()

