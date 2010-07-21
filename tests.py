
"""
  A collection of tests
"""
from time import sleep
import html

def log(s):
  print s

def append_ratios(table):
  ret = table
  t = table['values']
  ret['ratio'] = {}
  
  m = 0.0000001
  for k in t.keys():
    m = max(m, t[k])

  for k in t.keys():
    ret['ratio'][k] = '%.2f' % (ret['values'][k] / m)

  return ret

class IPerfOneToAllTest:
  """ 
    One to all iperf tests 
    Each iperf client outputs to a file, every 1 s
    during the test the (exp-moving?) average bandwidth it has
    received.  It is upto the test module to do whatever it wants
    with it.  Here, we will also monitor and collect the TCP window
    size every 1 second.  And finally, we also look at # TCP losses, 
    #TCP Timeouts and whatnot from /proc/net/netstat, which is
    /var/lib/vz/root/<id>/proc/1/net/netstat
  """
  
  def __init__(self, hosts, t=10):
    self.hosts = hosts
    self.t = t
    self.hostnames = [h.name for h in hosts]

    log('IPerf tests on pairs %s for %d seconds' % (self.hostnames, t))
    self.hosts[0].cmd('iperf -s &')

  def start(self):
    log('Starting iperf tests on pairs %s' % self.hostnames)

    for h1 in self.hosts[1:]:
      h1.cmd('rm -rf iperf_output tcpstats.csv')
      h1.cmd('mkdir -p iperf_output')
      h1.cmd('iperf -t %d -c %s -i 1 -yc > iperf_output/%s-%s &' 
        % (self.t, self.hosts[0].IP(), h1.name, self.hosts[0].name))
      h1.cmd('python tcpstats.py > tcpstats.csv &')

  def output(self):
    ret = ''
    start_time = 0
    for h in self.hosts:
      # time series data from iperf, 
      lines = h.open('iperf_output/%s-%s').readlines()
      bandwidth = ['Time,Bandwidth (Mbps)']
      
      for l in lines:
        arr = l.strip().split(',')
        tim,val = int(arr[0]), int(arr[-1])
        if start_time == 0:
          start_time = tim
        bandwidth.append( "%d,%.3f" % (tim - start_time, val*1.0/(2**20)) )
      
      ret += html.csv(bandwidth, "Bandwidth host %s" % (h.name))
      ret += html.csv(h.open('tcpstats.csv').readlines(), "TCP Window size host %s" % h.name)

  def end(self):
    #sleep(self.t) # we sleep till user wakes us up
    
    log('Ending iperf tests on hosts %s' % self.hostnames)
    # kill the iperf server
    self.hosts[0].cmd('killall -9 iperf')
    for h in self.hosts:
      h.cmd('killall -9 python')
    return self.output()


class IPerfAllPairTest:
  """ All Pairs iperf tests """

  def __init__(self, hosts, t=10):
    self.hosts = hosts
    self.t = t
    self.hostnames = [h.name for h in hosts]

    log('IPerf tests on pairs %s for %d seconds' % (self.hostnames, t))
    for h in hosts:
      h.cmd('iperf -s &')

  def start(self):
    log('Starting iperf tests on pairs %s' % self.hostnames)

    for h1 in self.hosts:
      h1.cmd('rm -rf iperf_output')
      h1.cmd('mkdir -p iperf_output')
      for h2 in self.hosts:
        if h1 != h2:
          h1.cmd('iperf -t %d -c %s > iperf_output/%s-%s &' 
              % (self.t, h2.IP(), h1.name, h2.name))
  
  def output(self):
    answer = {}
    aggregate_in = {}
    aggregate_out= {}
    for h in self.hosts:
      aggregate_in[h.name] = 0.0
      aggregate_out[h.name]=0.0

    for h1 in self.hosts:
      answer[h1.name] = {}
      for h2 in self.hosts:
        if h1 != h2:
          out = h1.open('iperf_output/%s-%s' % (h1.name, h2.name)).readlines()
          vals = out[-1].split(' ')[-2:]
          answer[h1.name][h2.name] = ' '.join(vals).strip().replace('bits/sec','')
          aggregate_in[h2.name] += float(vals[0])
          aggregate_out[h1.name] += float(vals[0])
        else:
          answer[h1.name][h2.name] = '----'
    
    IN = append_ratios({'values' : aggregate_in})
    OUT= append_ratios({'values' : aggregate_out})

    return '\n'.join([
      html.section("IPerf all pairs (%d sec)" % self.t, html.table(answer)),
      html.section("iperf aggregate IN", html.table(IN)),
      html.section("iperf aggregate OUT", html.table(OUT))
    ])

  def end(self):
    sleep(self.t+5)
    log('Ending iperf tests on hosts %s' % self.hostnames)
    for h in self.hosts:
      h.cmd('killall -9 iperf')
    
    return self.output()



class CPUStressTest:
  """ CPU stress test """

  def __init__(self, hosts):
    self.hosts = hosts
    self.hostnames = [h.name for h in hosts]

    log('CPU stress on %s' % self.hostnames)

  def start(self):
    log('Starting CPU stress on %s' % self.hostnames)

    for h in self.hosts:
      h.cmd('rm -rf cpu_stress_output')
      h.cmd('mkdir -p cpu_stress_output')
      h.cmd('cpu-stress > cpu_stress_output/%s &' % h.name)
  
  def output(self):
    ret = {'values':{}}

    for h in self.hosts:
      v =  int(h.open('cpu_stress_output/%s' % h.name).read().strip())
      ret['values'][h.name] = v

    return html.section("CPU Stress (seconds)", html.table(append_ratios(ret)))

  def end(self):
    log('Ending cpu-stress tests on %s' % self.hostnames)

    for h in self.hosts:
      h.cmd('killall cpu-stress')
    
    return self.output()

