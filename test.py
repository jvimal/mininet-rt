
from net import Mininet
from node import Host, Switch
from topo import SingleSwitchTopo

def main():
  topo = SingleSwitchTopo(10)
  m = Mininet(HostClass=Host, SwitchClass=Switch, topo=topo)
  
  m.start()
  #m.stop()
  #m.destroy()

main()

