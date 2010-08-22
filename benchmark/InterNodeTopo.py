#!/usr/bin/python

"""
"""

from mininet.topo import Topo, Node 

class InterNodeTopo( Topo ):
    '''Topology for a group of 2host-1sw sets.'''

    def __init__( self, N ):
	'''Constructor'''

	# Add default members to class.
	super( InterNodeTopo, self ).__init__()

	# Create switch and host nodes
	hosts = range(1, 2*N+1)
	switches = range(2*N+1, 3*N+1)
	for h in hosts:
	    self.add_node( h, Node( is_switch=False ) )
	for s in switches:
	    self.add_node( s, Node( is_switch=True ) )

	# Wire up hosts
	for i in range(0, N):
	    self.add_edge(hosts[2*i], switches[i])
	    self.add_edge(hosts[2*i + 1], switches[i])

	# Consider all switches and hosts 'on'
	self.enable_all()

if __name__ == '__main__':
    sizes = [ 1, 10, 20 ]
    for n in sizes:
	print "*** Printing InterNodeTopo : size ", n
	topo = InterNodeTopo(n)
	print "Nodes: ", topo.nodes()
	print "Switches: ", topo.switches()
	print "Hosts: ", topo.hosts()
	print "Edges: ", topo.edges()
