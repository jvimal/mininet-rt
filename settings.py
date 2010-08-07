"""
  Settings across modules in a central location.
  Initialised to default values.
"""
import getopt

# number of hosts
n = 3

# time to run tests
t = 10
# Let rate be none by default..
rate = None
outputfile = 'out.html'

# do we just start the hosts and pack?
detach = False

# just print the commands, useful for debugging
dryrun = False
test = ''
stop = False
# Unused as of now
tcpdump = False
veth = False
etun = True

cpulimit = None
cpulimit_switch= None
# switch container ids will start from 1000+
# 1001, ...
offset_switch_id = 1000


def set_options(argv):
  optlist, args = getopt.getopt(argv, 'n:t:r:o:dphT:', [
    'stop', 'tcpdump', 'dryrun',
    'test=', 'help', 'cpulimit='
  ])
  # prolly a better way of doing this...
  global n,t,rate,outputfile,detach,dryrun,test,\
    stop,tcpdump,veth,etun,cpulimit,cpulimit_switch,\
    offset_switch_id
  for (o,a) in optlist:
    if o == '-n':
      n = int(a)
    if o == '-t':
      t = int(a)
    if o == '-r':
      rate = a
      if a.lower() == 'none':
        rate = None
    if o == '-o':
      outputfile = a
    if o == '-d':
      detach = True
    if o == '--dryrun':
      dryrun = True
    if o == '-h' or o == '--help':
      printhelp()
      sys.exit(0)
    if o == '--test':
      test = a
    if o == '--stop':
      stop = True
    if o == '--tcpdump':
      tcpdump = True
    if o == '--cpulimit':
      cpulimit = int(a)
    if o == '--cpulimit_switch':
      cpulimit_switch = int(a)

  if outputfile == '':
    outputfile = 'results-%d-%d.html' % (n, t)
  
