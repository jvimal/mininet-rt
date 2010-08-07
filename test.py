
from net import Mininet
from node import Host, Switch, UserSwitch
from topo import SingleSwitchTopo, LinearTopo
from tests import IPerfOneToAllTest, CPUStressTest

import html
import sys
from time import sleep
import getopt
from termcolor import colored
import settings as s
from help import printhelp

def main():
  s.set_options(sys.argv[1:])
  topo = SingleSwitchTopo(s.n)
  m = Mininet(switch=UserSwitch, topo=topo, controller=None, rate=s.rate)
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
    prompt = colored('Without asking why, type 1 and RET when you want to stop: ', 'cyan')
    while True:
      x = int(raw_input(prompt))
      if x == 1:
        break
    
    if len(s.test):
      res = it.end()
    
      html.html(s.outputfile, html.comments([
        'test: %s' % (s.test),
        'topology: %s' % (topo),
      ]) + res)

  m.stop()
  # please don't do this unless really needed...
  #m.destroy()

main()

