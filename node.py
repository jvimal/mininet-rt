
"""
In contrast to mininet, there are no Switches
or Controller nodes.  Just an end host.
"""
import os
from util import run, ipStr, shell_cmd, Command
fileopen = open
from cmd import Cmd
import settings
from util import colored

def cmd(s, comment=None):
  if comment is not None:
    comment = colored('(%s)' % comment, 'green')
  else:
    comment = ''
  print '# %s %s' % (colored(s, 'yellow'), comment)
  if not settings.dryrun:
    shell_cmd(s)

class Node(object):
  def __init__(self,p):
    pass
  def start(self):
    pass

  def stop(self):
    pass

  def create(self):
    pass

  def destroy(self):
    pass

class Controller(Node):
  pass

class RemoteController(Node):
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
  
  def sendCmd(self, c):
    return self.send_command(c)

  def send_command(self, c):
    """
      send command c to this particular host
      and return a "command" handle that can 
      later be used to fetch output

      this is non blocking
    """
    return Command(["vzctl", "exec2", "%d" % self.id, c])

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
    """Destroy's the host's root directory.
    Please don't do it unless needed."""
    cmd("vzctl destroy %d" % self.id)


_next_bridgewire_id=0
def next_bridgewire_id():
  global _next_bridgewire_id
  _next_bridgewire_id += 1
  return _next_bridgewire_id

class UserSwitch(Node):
  """ Ideally this should be a subclass of a switch class
  but not for now."""
  
  def __init__(self,id):
    self.name  = 'sw%d' % (id)
    self.id = id
    # container's id
    self.cid = self.id + settings.offset_switch_id
    self.created = []
    self.create()
    self.ifaces = []
    self.bridgewires = []

  def create(self):
    """This will create a userspace switch, which is nothing 
    but a container with a switch process in it"""
    cmd("vzctl create %d --hostname %s --ostemplate debian-5.0-x86_64" % (self.cid, self.name))
    # useless thing, avoid copying again and again
    # maybe hook to a settings variable
    # TODO!! 
    files_to_copy = [
      "/home/jvimal/openflow/controller/controller",
      "/home/jvimal/openflow/udatapath/ofdatapath",
      "/home/jvimal/openflow/secchan/ofprotocol",
    ]
    dst_dir = "/var/lib/vz/private/%d/bin" % self.cid
    for f in files_to_copy:
      cmd("cp %s %s" % (f, dst_dir))

  def create_iface(self, insidename):
    """Just create an iface for the container and return its global
    name."""
    cmd("vzctl set %d --netif_add %s" % (self.cid, insidename), 
      "it's inside!")
    self.ifaces.append(insidename)
    outside_name = 'veth%d.%d' % (self.cid, len(self.ifaces))
    return outside_name

  def add_iface(self, node):
    """it's actually connect host's iface (node), bad choice of 
    naming this function. TODO: should change this!"""
    iface = node.ifaces[0][0]
    # add a corresponding interface to our switch
    # let's name it the same because, it doesn't matter
    # and it's useful to debug
    # it will be visible as veth<container_id>.<n> to the outside world
    outside_name = self.create_iface('in'+iface)
    
    bridgewire_name = 'br%d' % next_bridgewire_id()
    # this is the only new thing we've created.. a br<id>
    self.bridgewires.append(bridgewire_name)

    cmd("brctl addbr %s" % bridgewire_name)
    # bridge the iface and our **outside** iface
    # this is like the wire between the host and the switch
    cmd("brctl addif %s %s" % (bridgewire_name, outside_name))
    cmd("brctl addif %s %s" % (bridgewire_name, iface))
    
  def connect_switch(self, sw):
    # this becomes simple actually... 
    # no need for veth pair as in the normal switch case
    # just bridge the two interfaces that the switches anyway have!
    bridgewire_name = 'br%d' % next_bridgewire_id()
    cmd("brctl addbr %s" % bridgewire_name)
    # our interface goes to switch sw
    our_their_outside = self.create_iface(sw.name)
    their_our_outside = sw.create_iface(self.name)
    cmd("brctl addif %s %s" % (bridgewire_name, our_their_outside))
    cmd("brctl addif %s %s" % (bridgewire_name, their_our_outside))
    
    self.bridgewires.append(bridgewire_name)
    
  def configure(self):
    for br in self.bridgewires:
      cmd("ifconfig %s up" % br)
      cmd("ifconfig %s 0" % br)
    # let's initialise our own loopback
    # needed for the controller
    # let's just forget the case of having a
    # single controller. right now, every switch
    # has its own controller ;) 
    # need to worry about ip address and all that.. :-/
    self.cmd("ifconfig lo up")
    for iface in self.ifaces:
      self.cmd("ifconfig %s up" % iface)
    
    # make the tun device
    self.cmd("mkdir -p /dev/net")
    self.cmd("mknod /dev/net/tun c 10 200","enabling tun/tap for container")
    self.cmd("chmod 600 /dev/net/tun")

    self.cmd("controller -v ptcp: 2>&1 1> /tmp/controller.log &")
    intfs = ','.join( self.ifaces )
    self.cmd("ofdatapath --no-slicing -i %s punix:/tmp/ofsock 2>&1 1> /tmp/ofdp.log &" % intfs)
    self.cmd("ofprotocol unix:/tmp/ofsock tcp:127.0.0.1 2>&1 1> /tmp/ofp.log &")
  
  def cmd(self,c, comment=None):
    cmd("vzctl exec %d '%s'" % (self.cid, c), comment)

  def start(self):
    # should use the host's command interface to 
    # start the of switch process
    # self.cmd("ofprotocol blah blah")
    cmd("vzctl set %d --devices c:10:200:rw" % self.cid)
    cmd("vzctl set %d --capability net_admin:on" % self.cid)
    cmd("vzctl start %d" % (self.cid))

  def stop(self):
    for br in self.bridgewires:
      cmd("ifconfig %s down" % br)
    # no veths created...
    # but containers were created
    cmd("vzctl stop %d" % self.cid)

  def destroy(self):
    # will remove all its files
    cmd("vzctl destroy %d" % self.cid)

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
    name = '%s%s' % (self.name, sw.name)
    peer = '%s%s' % (sw.name, self.name)
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

