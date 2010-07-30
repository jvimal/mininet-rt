
"""
In contrast to mininet, there are no Switches
or Controller nodes.  Just an end host.
"""
import os
from util import run, ipStr, shell_cmd
fileopen = open
from cmd import Cmd
import settings

def cmd(s):
  print '# %s' % s
  if not settings.dryrun:
    shell_cmd(s)

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
    #self.shell = Cmd(self)

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
    cmd("vzctl exec %d '%s'" % (self.id, c))
    #self.shell.cmd(c)
  
  def open(self, file):
    # check if root fs is mounted.  if it is, then return 
    # that file.  else return from private dir
    fullpath1 = os.path.join("/var/lib/vz/root/%d" % self.id, file)
    fullpath2 = os.path.join("/var/lib/vz/private/%d" % self.id, file)
    print '# open %s' % fullpath1
    
    try:
      ret = fileopen(fullpath1)
    except:
      ret = fileopen(fullpath2)
    return ret

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
    self.created = []
    self.create()
    self.ifaces = []

  def create(self):
    cmd("brctl addbr %s" % self.name)
  
  def add_iface(self, node):
    iface = node.ifaces[0][0]
    cmd("brctl addif %s %s" % (self.name, iface))
    self.ifaces.append(iface)

  def connect_switch(self, sw):
    name = '%s.%s' % (self.name, sw.name)
    peer = '%s.%s' % (sw.name, self.name)
    #this command works ONLY on kernel versions 2.6.28+,
    # as it requires the veth module support.

    if settings.veth:
      cmd("ip link add name %s type veth peer name %s" % (name, peer))

    # with a patched 2.6.18 kernel having etun
    # support, we should have something similar setup
    # patch here: http://lwn.net/Articles/229677/
    # i'll arrange a standalone patch shortly
    elif settings.etun:
      cmd("echo -n '%s,%s' > /sys/module/etun/parameters/newif" % (name, peer))
    else:
      print '*** Cannot proceed.  Need support for virtual ethernet pair'
      print '*** to create (%s,%s)' % (name, peer)

    cmd("ifconfig %s up" % name)
    cmd("ifconfig %s up" % peer)
    cmd("brctl addif %s %s" % (self.name, name))
    self.ifaces.append(name)

    cmd("brctl addif %s %s" % (sw.name, peer))
    sw.ifaces.append(peer)
    
    self.created += [name] # It's enough to delete one of the pairs

  def configure(self):
    cmd("ifconfig %s 0" % self.name)

  def stop(self):
    # TODO: should we delif's first?
    # We should do it at least for the links we create..
    # The hosts will take care of the rest
    for iface in self.created:
      cmd("ifconfig %s down" % iface)
      
      if settings.veth:
        cmd("ip link del dev %s" % iface)
      else:
        cmd("echo -n '%s' > /sys/module/etun/parameters/delif" % iface)

    cmd("ifconfig %s down" % self.name)
    cmd("brctl delbr %s" % self.name)

