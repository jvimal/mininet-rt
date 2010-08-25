#!/usr/bin/python

"""
Tests for CPU isolation.
"""

import sys
flush = sys.stdout.flush
from time import sleep

from mininet.net import init, Mininet
from mininet.node import OVSKernelSwitch, Controller
from mininet.util import getCmd
from mininet.log import lg
from InterNodeTopo import *
from IntraNodeTopo import *
from Parser import *

bmarkToTopo = {'inter':(lambda n: InterNodeTopo(n)), 'intra':(lambda n: IntraNodeTopo(n))}

def BWIsolation(bmark, N, runs):

    "Check bandwidth isolation for various topology sizes."

    cpustress = 'cpu/cpu-stress'
    net = Mininet(topo=bmarkToTopo[bmark](N), switch=OVSKernelSwitch, 
        controller=Controller, autoSetMacs=True, autoStaticArp=False, 
        hostCPUFrac=0.2, hostCPUPeriod=500)
    net.start()
    n = 2*N

    for _ in xrange(0, runs):
        result = [''] * n
        cmd = [None] * n

        #start the cpu-stressers
        for i in xrange(0, n):
            server = net.hosts[i]
            scmd = cpustress + ' 10 0' # 10 second run
            cmd[i] = server.lxcSendCmd(scmd)

        #fetch the results
        for i in xrange(0, n):
            c = cmd[i].waitOutput()
            try:
                result[i] = c.split('\n')[1].replace(',',':')
            except:
                result[i] = 'NaN'

        print ','.join(result)
        flush()

    net.stop()

def usage():
    print >> sys.stderr, "Usage: python %s inter|intra" % sys.argv[0]
    exit(1)

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        usage()
    sizes = [10, 20, 40, 80 ]
    trials = 10
    for bm in bmarkToTopo.keys():
        if(re.match(bm, sys.argv[1], re.I) is not None):
            #lg.setLogLevel( 'debug' )
            init()
            print >> sys.stderr, "#*** Running %s-node CPUIsolation Benchmark ***" % bm
            for n in sizes:
                print >> sys.stderr, "#Size :", n
                BWIsolation(bm, n, trials)
            exit(0)
    usage()
