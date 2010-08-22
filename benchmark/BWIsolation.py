#!/usr/bin/python

"""
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

    cliout = [''] * N
    iperf = getCmd('iperf')
    net = Mininet(topo=bmarkToTopo[bmark](N), switch=OVSKernelSwitch, controller=Controller, autoSetMacs=True, autoStaticArp=True)
    net.start()

    for _ in range(0, runs):
        result = [''] * N
        servercmd = [None] * N
        clientcmd = [None] * N

        #start the servers
        for n in range(0, N):
            server = net.hosts[2*n + 1]
            scmd = iperf + ' -yc -s'
            servercmd[n] = server.lxcSendCmd(scmd)

        sleep(1)
        
        #start the clients
        for n in range(0, N):
            client, server = net.hosts[2*n], net.hosts[2*n + 1]
            ccmd = iperf + ' -yc -t 10 -c ' + server.IP()
            clientcmd[n] = client.lxcSendCmd(ccmd)

        #fetch the client and server results
        for n in range(0, N):
            c = clientcmd[n].waitOutput()
            cliout[n] = c
            try:
                result[n] = str(getBandwidth(cliout[n]))
            except Exception:
                result[n] = 'NaN'
            servercmd[n].kill()
            servercmd[n].wait()

        print ','.join(result)
        flush()

    net.stop()

def usage():
    print >> sys.stderr, "Usage: python BWIsolation inter|intra"
    exit(1)

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        usage()
    #sizes = [ 1, 2, 3, 5, 10, 20, 40 ]
    sizes = [ 1, 2]
    trials = 3
    for bm in bmarkToTopo.keys():
        if(re.match(bm, sys.argv[1], re.I) is not None):
            lg.setLogLevel( 'error' )
            init()
            print >> sys.stderr, "#*** Running %s-node BWIsolation Benchmark ***" % bm
            for n in sizes:
                print >> sys.stderr, "#Size :", n
                BWIsolation(bm, n, trials)
            exit(0)
    usage()
