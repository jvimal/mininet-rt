
"""
Simple topology related data structures

A topology is just a graph of nodes and 
edge information.  nodes can only be hosts
or switches.
"""

class Node:
  def __init__(self, id, is_switch=False):
    self.id = id
    self.is_switch = is_switch
  
  def __cmp__(self,other):
    return self.id - other.id

class Topo(object):
  def __init__(self):
    self.nodes = []
    self.edges = []

  def add_node(self, n):
    self.nodes.append(n)

  def add_edge(self, u, v):
    self.edges.append((u,v))


class SingleSwitchTopo(Topo):
  def __init__(self, k=2):
    super(SingleSwitchTopo, self).__init__()
    self.k = k
    s = Node(1, is_switch=True)

    self.add_node(s)
    hosts = range(2, k+2)

    for h in hosts:
      n = Node(h)
      self.add_node(n)
      self.add_edge(n, s)
  
  def __str__(self):
    return '%s(%s)' % ('SingleSwitchTopo', self.k)

class LinearTopo(Topo):
  def __init__(self,k=2):
    super(LinearTopo, self).__init__()
    self.k = k
    
    sws = range(1, k+1)
    for s in sws:
      h = s + k
      sw = Node(s, is_switch=True)
      ho = Node(h)
      self.add_node(sw)
      self.add_node(ho)
      self.add_edge(sw, ho)
      if s > 1:
        self.add_edge(Node(s-1, is_switch=True), sw)

  def __str__(self):
    return '%s(%s)' % ('LinearTopo', self.k)

