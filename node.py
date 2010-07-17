
"""
In contrast to mininet, there are no Switches
or Controller nodes.  Just an end host.
"""

from util import run

def cmd(s):
  print '# %s' % s
  #run(s)


class Node(object):
  def start(self):
    pass

  def stop(self):
    pass

  def create(self):
    pass

  def destroy(self):
    pass


class Host(Node):
  def __init__(self,id):
    self.id = id
    self.name = 'h%d' % id
    self.ifaces = []
    # Create scratch area if not there already
    self.create()
  
  def create(self):
    cmd("vzctl create %d --hostname %s --ostemplate debian-5.0-x86_64" % (self.id, self.name))
    self.add_iface()

  def start(self):
    cmd("vzctl start %d" % self.id)

  def stop(self):
    cmd("vzctl stop %d" % self.id)

  def cmd(self, cmd):
    cmd("vzctl exec %d %s" % (id, cmd))
  
  def add_iface(self):
    next_iface_id = len(self.ifaces)
    veth = 'veth%d.%d' % (self.id, next_iface_id)
    eth = 'eth%d' % next_iface_id
    self.ifaces.append((veth, eth))
    cmd("vzctl set %d --netif_add eth%d" % (self.id, next_iface_id))
  
  def del_iface(self):
    pass

  def destroy(self):
    cmd("vzctl destroy %d" % self.id)


class Switch(Node):
  def __init__(self,id):
    # This will be a bridge sw<id>
    self.name = 'sw%d' % id
    self.id = id
    self.create()
    self.ifaces = []

  def create(self):
    cmd("brctl addbr %s" % self.name)
  
  def add_iface(self, node):
    iface = node.ifaces[0][0]
    cmd("brctl addif %s %s" % (self.name, iface))
    self.ifaces.append(iface)

  def destroy(self):
    # TODO: should we delif's first?
    cmd("brctl delbr %s" % self.name)


