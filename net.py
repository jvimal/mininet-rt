
"""
Networking is setup as follows:
* All guests are created with a veth device;
  the host end is called veth<id>.0
  the guest end is called eth0
  IP address is 10.0.0.0+<id>
* A 'switch' with some hosts connected to it
  can be seen as a "bridge" between those devices
* switch <-> switch connection is also possible
  this makes it possible to create interesting 
  topologies
"""

import os, sys
from util import run, shell_cmd, shell_output
from time import sleep

def cmd(s):
  print '# %s' % s
  run(s)

class Mininet:

  def __init__(self, HostClass, SwitchClass, topo):
    if os.getuid() != 0:
      print 'Please run as root.'
      sys.exit(-1)

    self.host = HostClass
    self.switch = SwitchClass
    
    self.next_host_id = 1
    self.next_switch_id = 1

    self.hosts = []
    self.switches = []
    self.controllers = []
    self.name_to_node = {}

    self.topo = topo

  def add_host(self, name=None):
    """ Adds a host to the network with given properties """
    host = self.host(self.next_host_id)
    if name is None:
      name = 'h%d' % self.next_host_id
    host.name = name
    self.hosts.append(host)
    
    self.name_to_node[name] = host

    self.next_host_id+=1
    return host

  def add_switch(self):
    """
      It can be a kernel switch, a user switch, or just
      a simple Linux bridge.  Let's go with bridge for
      now
    """
    sw = self.switch(self.next_switch_id)
    self.switches.append(sw)

    self.name_to_node[sw.name] = sw

    self.next_switch_id += 1
    return sw

  def add_controller(self, controller):
    """ Add an OF controller, ONLY IF we use an OF switch """
    pass
 
  def configure_hosts(self):
    for host in self.hosts:
      # Add IP address; for now, each host has only one eth0 interface
      # Add default route
      host.configure()

  def configure_switches(self):
    for s in self.switches:
      s.configure()

  def build_topology(self, topo):
    self.ids_to_nodes = {}
    self.topo = topo

    for n in topo.nodes:
      if n.is_switch:
        s = self.add_switch()
        self.ids_to_nodes[n.id] = s
      else:
        h = self.add_host()
        h.start()
        self.ids_to_nodes[n.id] = h

    def create_link(u, v):
      su = self.ids_to_nodes[u.id]
      sv = self.ids_to_nodes[v.id]
      if u.is_switch and v.is_switch:
        # we need to one interface and add them
        # to both the bridges
        # should check if this is possible
        su.connect_switch(sv)
      if not u.is_switch and v.is_switch:
        # u already has an iface
        # just add that iface onto v's bridge
        sv.add_iface(su)
      if u.is_switch and not v.is_switch:
        # ditto, but with v
        su.add_iface(sv)
      else:
        # both are hosts, connected by wire
        # not allowed for now
        # one solution is to create a temporary
        # bridge and connect the two
        pass

    # create the edges
    for (u,v) in self.topo.edges:
      create_link(u, v)
    
  def configure_rates(self):
    # all veth<id>.0 devices get 100Mbps
    # same for all switches
    
    cmd("tc qdisc del dev veth1.0 root")
    cmd("tc qdisc add dev veth1.0 root handle 1:0 htb default 10")
    cmd("iptables -t mangle -F")
    l = len(self.hosts)
    for i,h in zip(range(1,l+1), self.hosts):
      # add the policy
      cmd("tc class add dev veth%d.0 parent 1:0 classid 1:%d htb rate 100mbit burst 15k"% (1, i))
      cmd("tc class add dev veth%d.0 parent 1:0 classid 1:%d htb rate 100mbit burst 15k"% (1, l+i))
      
      # create the filter
      cmd("iptables -t mangle -A PREROUTING -i veth%d.0 -j MARK --set-mark %d" % (i, i))
      cmd("iptables -t mangle -A PREROUTING -i veth%d.0 -j RETURN" % (i))
      
      cmd("iptables -t mangle -A POSTROUTING -o veth%d.0 -j MARK --set-mark %d" % (i, l+i))
      cmd("iptables -t mangle -A POSTROUTING -o veth%d.0 -j RETURN" % (i))
      
      # now tell tc that we mark packets in iptables
      cmd("tc filter add dev veth1.0 parent 1:0 protocol ip prio 1 handle %d fw classid 1:%d" % (i, i))
      cmd("tc filter add dev veth1.0 parent 1:0 protocol ip prio 1 handle %d fw classid 1:%d" % (i+l, i+l))
      
      # attach a SFQ at the end of every chain
      cmd("tc qdisc add dev veth%d.0 parent 1:%d handle %d:0 sfq perturb 10" % (1, i, i))
      cmd("tc qdisc add dev veth%d.0 parent 1:%d handle %d:0 sfq perturb 10" % (1, i+l, i+l))


  def start(self):
    """ Boot up all the hosts """
    self.build_topology(self.topo)
    self.configure_switches()
    self.configure_hosts()
    # Wait for hosts to boot up
    self.wait_for_hosts()
    self.configure_rates()

  def wait_for_hosts(self):
    l = len(self.hosts)
    while True:
      print 'Waiting for hosts to boot..', 
      sys.stdout.flush()
      sleep(10)
      n = int(shell_output('vzlist -a | grep running | wc -l').strip())
      print '%d/%d' % (n, l)
      if n == l:
        break
  
  def stop(self):
    """ Shutdown all the hosts """
    for h in self.hosts:
      h.stop()
    
    # remove the bridges
    for s in self.switches:
      s.stop()

    # remove iptables/tc queues
    cmd("iptables -t mangle -F")
    cmd("tc qdisc del dev veth1.0 root")
    # ^^ This should hopefully remove all the
    # classes/queues under it too

  def destroy(self):
    """ Clean up mininet instances """
    for h in self.hosts:
      h.destroy()

    for s in self.switches:
      s.destroy()

    self.destroy_links()

