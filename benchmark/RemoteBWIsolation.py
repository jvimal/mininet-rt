#!/usr/bin/python

"""
Tests Bandwidth isolation of mininet-rt remotely
"""

import sys
flush = sys.stdout.flush
from time import sleep

from mininet.mnmaster import MininetMasterService
from InterNodeTopo import *
from IntraNodeTopo import *
from Parser import *

bmarkToTopo = {'inter':(lambda n: InterNodeTopo(n)), 'intra':(lambda n: IntraNodeTopo(n))}

def BWIsolation(bmark, N, runs):

    "Check bandwidth isolation for various topology sizes."

    cliout = [''] * N
    master = MininetMasterService()
    master.mininetStart(bmarkToTopo[bmark](N), ('127.0.0.1', 6633))
    hosts = master.mininetGetHosts()

    for _ in range(0, runs):
        result = [''] * N
        servercmd = [None] * N
        clientcmd = [None] * N

        #start the servers
        for n in range(0, N):
            server = hosts[2*n + 1]
            iperf = master.getCmd(server, 'iperf')
            scmd = iperf + ' -yc -s'
            servercmd[n] = master.cmdSend(server, scmd)

        sleep(1)
        
        #start the clients
        for n in range(0, N):
            client, server = hosts[2*n], hosts[2*n + 1]
            iperf = master.getCmd(client, 'iperf')
            ccmd = iperf + ' -yc -t 10 -c ' + master.getHostIP(server)
            clientcmd[n] = master.cmdSend(client, ccmd)

        #fetch the client and server results
        for n in range(0, N):
            client, server = hosts[2*n], hosts[2*n + 1]
            c = master.cmdWaitOutput(client, clientcmd[n])
            cliout[n] = c
            try:
                result[n] = str(getBandwidth(cliout[n]))
            except Exception:
                result[n] = 'NaN'
            master.cmdKill(server, servercmd[n])
            master.cmdWait(server, servercmd[n])

        print ','.join(result)
        flush()

    master.mininetStop()

def usage():
    print >> sys.stderr, "Usage: python BWIsolation inter|intra"
    exit(1)

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        usage()
    sizes = [1,] # [ 1, 2, 3, 5, 10, 20, 40, 80 ]
    trials = 3
    for bm in bmarkToTopo.keys():
        if(re.match(bm, sys.argv[1], re.I) is not None):
            print >> sys.stderr, "#*** Running %s-node BWIsolation Benchmark ***" % bm
            for n in sizes:
                print >> sys.stderr, "#Size :", n
                BWIsolation(bm, n, trials)
            exit(0)
    usage()
