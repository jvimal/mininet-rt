"Utility functions for Mininet."

from time import sleep
from resource import setrlimit, RLIMIT_NPROC, RLIMIT_NOFILE
import select
from subprocess import call, check_call, Popen, PIPE, STDOUT

from log import lg

def no_cores():
  return 2

class Command:

  def __init__(self, c):
    self.cmd = c
    self.p = Popen(c, stdout=PIPE, stdin=PIPE, stderr=PIPE)

  def read_full(self):
    # warning, will BLOCK until we read all output
    return self.p.communicate()[0]

  def readn(self, n):
    toread = n
    data = ''
    while toread:
      data = self.p.stdout.read(toread)
      toread -= len(data)
    return data

  def readline(self):
    return self.p.stdout.readline()

  def write(self, data):
    """
      There might be cases where you might want to 
      write() data into the program. e.g., you've 
      spawned a shell and you write a command to it,
      it will be interpreted by the shell
    """
    self.p.stdin.write(data)

  def writeline(self, data):
    self.write(data + '\n')

  def poll(self):
    """ 
      poll checks if our command has terminated.
      if yes, then returns the return code
      else dunno what it does; python doc doesn't tell.
      but it's non blocking
    """
    return self.p.poll()

  def wait(self):
    return self.p.wait()
  
  def kill(self):
    return self.p.kill()
  
  def signal(self, signal):
    return self.p.send_signal(signal)


def run( cmd ):
    """Simple interface to subprocess.call()
       cmd: list of command params"""
    return call( cmd.split( ' ' ) )

def checkRun( cmd ):
    """Simple interface to subprocess.check_call()
       cmd: list of command params"""
    return check_call( cmd.split( ' ' ) )

def shell_output(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    return p.communicate()[0]

def shell_cmd(cmd):
    ret = call(cmd, shell=True)
    return ret

def quietRun( cmd ):
    """Run a command, routing stderr to stdout, and return the output.
       cmd: list of command params"""
    if isinstance( cmd, str ):
        cmd = cmd.split( ' ' )
    popen = Popen( cmd, stdout=PIPE, stderr=STDOUT )
    # We can't use Popen.communicate() because it uses
    # select(), which can't handle
    # high file descriptor numbers! poll() can, however.
    output = ''
    readable = select.poll()
    readable.register( popen.stdout )
    while True:
        while readable.poll():
            data = popen.stdout.read( 1024 )
            if len( data ) == 0:
                break
            output += data
        popen.poll()
        if popen.returncode != None:
            break
    return output

# Interface management
#
# Interfaces are managed as strings which are simply the
# interface names, of the form 'nodeN-ethM'.
#
# To connect nodes, we create a pair of veth interfaces, and then place them
# in the pair of nodes that we want to communicate. We then update the node's
# list of interfaces and connectivity map.
#
# For the kernel datapath, switch interfaces
# live in the root namespace and thus do not have to be
# explicitly moved.

def makeIntfPair( intf1, intf2 ):
    """Make a veth pair connecting intf1 and intf2.
       intf1: string, interface
       intf2: string, interface
       returns: success boolean"""
    # Delete any old interfaces with the same names
    quietRun( 'ip link del ' + intf1 )
    quietRun( 'ip link del ' + intf2 )
    # Create new pair
    cmd = 'ip link add name ' + intf1 + ' type veth peer name ' + intf2
    return quietRun( cmd )

def retry( retries, delaySecs, fn, *args, **keywords ):
    """Try something several times before giving up.
       n: number of times to retry
       delaySecs: wait this long between tries
       fn: function to call
       args: args to apply to function call"""
    tries = 0
    while not fn( *args, **keywords ) and tries < retries:
        sleep( delaySecs )
        tries += 1
    if tries >= retries:
        lg.error( "*** gave up after %i retries\n" % tries )
        exit( 1 )

def moveIntfNoRetry( intf, node, printError=False ):
    """Move interface to node, without retrying.
       intf: string, interface
       node: Node object
       printError: if true, print error"""
    cmd = 'ip link set ' + intf + ' netns ' + repr( node.pid )
    quietRun( cmd )
    links = node.cmd( 'ip link show' )
    if not intf in links:
        if printError:
            lg.error( '*** Error: moveIntf: ' + intf +
                ' not successfully moved to ' + node.name + '\n' )
        return False
    return True

def moveIntf( intf, node, printError=False, retries=3, delaySecs=0.001 ):
    """Move interface to node, retrying on failure.
       intf: string, interface
       node: Node object
       printError: if true, print error"""
    retry( retries, delaySecs, moveIntfNoRetry, intf, node, printError )

def createLink( node1, node2, port1=None, port2=None ):
    """Create a link between nodes, making an interface for each.
       node1: Node object
       node2: Node object
       port1: node1 port number (optional)
       port2: node2 port number (optional)
       returns: intf1 name, intf2 name"""
    return node1.linkTo( node2, port1, port2 )

def fixLimits():
    "Fix ridiculously small resource limits."
    setrlimit( RLIMIT_NPROC, ( 4096, 8192 ) )
    setrlimit( RLIMIT_NOFILE, ( 16384, 32768 ) )

def _colonHex( val, bytes ):
    """Generate colon-hex string.
       val: input as unsigned int
       bytes: number of bytes to convert
       returns: chStr colon-hex string"""
    pieces = []
    for i in range( bytes - 1, -1, -1 ):
        piece = ( ( 0xff << ( i * 8 ) ) & val ) >> ( i * 8 )
        pieces.append( '%02x' % piece )
    chStr = ':'.join( pieces )
    return chStr

def macColonHex( mac ):
    """Generate MAC colon-hex string from unsigned int.
       mac: MAC address as unsigned int
       returns: macStr MAC colon-hex string"""
    return _colonHex( mac, 6 )

def ipStr( ip ):
    """Generate IP address string from an unsigned int.
       ip: unsigned int of form w << 24 | x << 16 | y << 8 | z
       returns: ip address string w.x.y.z, or 10.x.y.z if w==0"""
    w = ( ip & 0xff000000 ) >> 24
    w = 10 if w == 0 else w
    x = ( ip & 0xff0000 ) >> 16
    y = ( ip & 0xff00 ) >> 8
    z = ip & 0xff
    return "%i.%i.%i.%i" % ( w, x, y, z )

def ipNum( w, x, y, z ):
    """Generate unsigned int from components ofIP address
       returns: w << 24 | x << 16 | y << 8 | z"""
    return  ( w << 24 ) | ( x << 16 ) | ( y << 8 ) | z

def ipParse( ip ):
    "Parse an IP address and return an unsigned int."
    args = [ int( arg ) for arg in ip.split( '.' ) ]
    return ipNum( *args )

def checkInt( s ):
    "Check if input string is an int"
    try:
        int( s )
        return True
    except ValueError:
        return False

def checkFloat( s ):
    "Check if input string is a float"
    try:
        float( s )
        return True
    except ValueError:
        return False

def makeNumeric( s ):
    "Convert string to int or float if numeric."
    if checkInt( s ):
        return int( s )
    elif checkFloat( s ):
        return float( s )
    else:
        return s

# pylint: disable-msg=E1101,W0612

def isShellBuiltin( cmd ):
    "Return True if cmd is a bash builtin."
    if isShellBuiltin.builtIns is None:
        isShellBuiltin.builtIns = quietRun( 'bash -c enable' )
    space = cmd.find( ' ' )
    if space > 0:
        cmd = cmd[ :space]
    return cmd in isShellBuiltin.builtIns

isShellBuiltin.builtIns = None

# pylint: enable-msg=E1101,W0612
