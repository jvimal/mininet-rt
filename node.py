
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
    # Create scratch area if not there already
    self.create()
    self.ifaces = []
  
  def create(self):
    cmd("vzctl create %d" % self.id)

  def start(self):
    cmd("vzctl start %d" % self.id)

  def stop(self):
    cmd("vzctl stop %d" % self.id)

  def cmd(self, cmd):
    cmd("vzctl exec %d %s" % (id, cmd))
  
  def add_iface(self):
    next_iface_id = len(self.ifaces)
    self.ifaces.append('eth%d' % next_iface_id)
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

  def destroy(self):
    cmd("brctl delbr %s" % self.name)


