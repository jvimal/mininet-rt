#!/usr/bin/python

"""
"""

import sys
flush = sys.stdout.flush

from mininet.net import init, Mininet
from mininet.node import UserSwitch, RemoteController
from mininet.topo import Topo, Node
from mininet.log import lg
from IntraNodeTopo import *
from Parser import *
from DataLog import *
import time

def IntraNodeBWIsolation(N, runs):

    "Check bandwidth isolation for various topology sizes."

    Switch = UserSwitch
    controller = lambda a: RemoteController(a)
    servout = [''] * N
    cliout = [''] * N
    net = Mininet(topo=InterNodeTopo(N), switch=Switch, controller=controller,
	    xterms=False, autoStaticArp=True)
    dl = DataLog("intra-node-bw-isolation.csv", "a", "csv")
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
	    server.sendCmd('iperf -s', printPid=True)
	    while server.lastPid is None:
		servout[n] += server.monitor()
	    #print "server.lastPid =", server.lastPid

	#start the clients
	for n in range(0, N):
	    client, server = net.hosts[2*n], net.hosts[2*n + 1]
	    #print "Client trying to connect to ", server.IP()
	    cmd = 'iperf -t 20 -c ' + server.IP()
	    #print cmd
	    client.sendCmd(cmd)

	#fetch the client and server results
	for n in range(0, N):
	    client, server = net.hosts[2*n], net.hosts[2*n + 1]
	    cliout[n] += client.waitOutput()
	    server.sendInt()
	    servout[n] += server.waitOutput()

	#parse the results
	for n in range(0, N):
	    try:
		result[n] = net._parseIperf(cliout[n])
	    except Exception:
		result[n] = "NaN"

	result = [getBandwidth(x) for x in result]
	dl.logList(result)
	#print cliout
	#print servout
	flush()
    dl.close()
    net.stop()


if __name__ == '__main__':
    lg.setLogLevel( 'warning' )
    init()
    #sizes = [ 1, 2, 3, 5, 10, 20, 40 ]
    sizes = [ 40, ]
    trials = 4
    print "*** Running IntraNodeBWIsolation Benchmark ***"
    for n in sizes:
	#print "Size : ", n
	IntraNodeBWIsolation(n, trials)
