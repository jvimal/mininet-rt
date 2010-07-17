
from net import Mininet
from node import Host, Switch

def main():
  m = Mininet(HostClass=Host, SwitchClass=Switch)
  m.add_host('a')
  m.add_host('b')
  m.add_switch()

  m.start()
  m.stop()
  m.destroy()

main()

