#!/usr/bin/python

"""
"""

import sys
flush = sys.stdout.flush
sys.path = ['/home/jvimal'] + sys.path

from mininet.net import init, Mininet
from mininet.node import Switch, RemoteController
#from mininet.topo import Topo, Node
from mininet.log import lg
from InterNodeTopo import *
from Parser import *
from DataLog import *

def InterNodeBWIsolation(N, runs):

    "Check bandwidth isolation for various topology sizes."

    controller = lambda a: RemoteController(a)
    servout = [''] * N
    cliout = [''] * N
    net = Mininet(topo=InterNodeTopo(N), switch=Switch, controller=controller)
        #xterms=False, autoStaticArp=True)
    dl = DataLog("inter-node-bw-isolation.csv", "a", "csv")
    dl.init()

    #net.interact()
    #return

    net.start()

    for i in range(0, runs):
        result = [0] * N

    for n in range(0, N):
        client, server = net.hosts[2*n], net.hosts[2*n + 1]
        #print client.IP(),",", client.MAC(), " <-> ", server.IP(), ",", \
            #  server.MAC()
        #print client.cmd('ping -c 3 ' + server.IP(), verbose=False)
    

    #start the servers
    for n in range(0, N):
        server = net.hosts[2*n + 1]
        #print "Starting iperf server on : ", server.IP()
        server.sendCmd('iperf -s')
        #while server.lastPid is None:
        #    servout[n] += server.monitor()
        #print "server.lastPid =", server.lastPid
    
    clientcmd = [None] * N
    #start the clients
    for n in range(0, N):
        client, server = net.hosts[2*n], net.hosts[2*n + 1]
        #print "Client trying to connect to ", server.IP()
        cmd = 'iperf -yc -t 20 -c ' + server.IP()
        #print cmd
        clientcmd[n] = client.sendCmd(cmd)

    #fetch the client and server results
    for n in range(0, N):
        client, server = net.hosts[2*n], net.hosts[2*n + 1]
        cliout[n] += clientcmd[n].waitOutput()
        #server.sendInt()
        #servout[n] += server.waitOutput()

    #parse the results
    for n in range(0, N):
        try:
            result[n] = getBandwidth(cliout[n])
        except Exception:
            result[n] = "NaN"

    dl.logList(result)
    #print cliout
    #print servout
    flush()
    dl.close()
    net.stop()


if __name__ == '__main__':
    lg.setLogLevel( 'warning' )
    init()
    sizes = [ 1 , 2, 3, 5, 10] #, 20, 40 ]
    trials = 3
    print "*** Running InterNodeBWIsolation Benchmark ***"
    for n in sizes:
    #print "Size : ", n
        InterNodeBWIsolation(n, trials)
