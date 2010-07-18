
"""
In contrast to mininet, there are no Switches
or Controller nodes.  Just an end host.
"""
import os
from util import run, ipStr
fileopen = open

def cmd(s):
  print '# %s' % s
  run(s)


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

  def start(self):
    cmd("vzctl start %d" % self.id)
    self.add_iface()

  def stop(self):
    cmd("vzctl stop %d" % self.id)

  def configure(self, ip=None, mask=None):
    # bring up the eth0 and set ip address
    if ip is None:
      # 10.0.0.0 + id
      ip = ipStr(self.id)
      mask = 8
    cmd("vzctl exec %d ifconfig eth0 %s/%s" % (self.id, ip, mask))
    self.ip = ip
    self.mask = mask

  def IP(self):
    return self.ip

  def cmd(self, c):
    cmd("vzctl exec %d %s" % (self.id, c))
  
  def open(self, file):
    fullpath = os.path.join("/var/lib/vz/private/%d" % self.id, file)
    print '# open %s' % fullpath
    return fileopen(fullpath)

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

  def configure(self):
    cmd("ifconfig %s 0" % self.name)

  def stop(self):
    # TODO: should we delif's first?
    cmd("brctl delbr %s" % self.name)

