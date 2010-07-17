
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

class Mininet:

  def __init__(self, HostClass, SwitchClass):
    self.host = HostClass
    self.switch = SwitchClass
    
    self.next_host_id = 0
    self.next_switch_id = 0

    self.hosts = []
    self.switches = []
    self.controllers = []

  def add_host(self):
    """ Adds a host to the network with given properties """
    host = self.host(self.next_host_id)
    self.next_host_id+=1
    
    self.hosts.append(host)
    return host

  def add_switch(self, id):
    """
      It can be a kernel switch, a user switch, or just
      a simple Linux bridge.  Let's go with bridge for
      now
    """
    sw = self.switch(self.next_switch_id)
    self.next_switch_id += 1

    self.switches.append(sw)
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
    # nothing to be done as of now
    pass
  
  def build_topology(self, topo):
    pass
  
  def start(self):
    """ Boot up all the hosts """
    for h in self.hosts:
      h.start()

  def stop(self):
    """ Shutdown all the hosts """
    for h in self.hosts:
      h.stop()
  
  def destroy(self):
    """ Clean up mininet instances """
    for h in self.hosts:
      h.destroy()

    for s in self.switches:
      s.destroy()

    self.destroy_links()

