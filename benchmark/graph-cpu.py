
import numpy as np
import matplotlib as m
m.use("Agg")
import matplotlib.pyplot as plt
import sys
import math

def read_values(fname):
    """ Returns a dict where the key is the number
    of nodes and values are the lists of result values """
    lines = open(fname).read().strip().split('\n')
    ret = {}
    for l in lines:
        if l.startswith('#'):
            continue
        vals = l.split(',')
        n = len(vals)
        if not ret.has_key(n):
            ret[n] = []
        ret[n].append(vals)
    return ret

def plot(n, lst):
    """ Plot for a given number of nodes and the
    bw numbers."""
    avg = 0.0
    std = 0.0
    ntrials = 0
    for l in lst:
        ntrials += 1
        avg += sum(l) / n
        std += np.std(l, dtype=np.float64)
    avg /= ntrials
    std /= ntrials

    return {
        'n': n,
        'avg': avg,
        'std': std,
    }

if len(sys.argv) != 2:
    print 'Usage: python %s csvfile' % sys.argv[0]
    print 'Will output graph to csvfile.png'
    sys.exit(0)

fname = sys.argv[1]
vals = read_values(fname)
fig = plt.figure(figsize=(8*2, 6), dpi=100)

def subplot(loc, ylabel, xlabel, offset):
    ax = fig.add_subplot(*loc)
    xlabels = []
    yvalues = []
    yerr = []

    N = 0
    for v in sorted(vals.keys()):
        # x[-1] is the user elapsed time
        # [-2] is the latency
        bar = plot(
            v, 
            map(lambda x: 
                map(lambda y: 
                    float(y.split(':')[offset]), x), vals[v]))
        N += 1
        xlabels.append(v)
        yvalues.append(bar['avg'])
        yerr.append(bar['std'] * 1.96) # 1.96 sigma ~ 95% CI

    ax.bar(range(N), yvalues, yerr=yerr, facecolor='#777777', align='center', ecolor='black')
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xticks(range(N))
    ax.set_title(sys.argv[1])
    ax.set_xticklabels(xlabels)


subplot((1,2,1),'elapsed user time', '# nodes', -1)
subplot((1,2,2),'timer latency', '# nodes', -2)

outfile = '%s.png' % fname
plt.savefig(outfile)
print 'saved to %s' % (outfile)
