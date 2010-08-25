
import numpy as np
import matplotlib as m
m.use("Agg")
import matplotlib.pyplot as plt
import sys

def read_values(fname):
    """ Returns a dict where the key is the number
    of nodes and values are the lists of result values """
    lines = open(fname).read().strip().split('\n')
    ret = {}
    for l in lines:
        if l.startswith('#'):
            continue
        vals = map(float, l.split(','))
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
    print 'Will output graph to csvfile.svg'
    sys.exit(0)

fname = sys.argv[1]
vals = read_values(fname)
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xlabels = []
yvalues = []
yerr = []

N = 0
for v in sorted(vals.keys()):
    bar = plot(v, vals[v])
    N += 1
    xlabels.append(v)
    yvalues.append(bar['avg'])
    yerr.append(bar['std'] * 1.96 / math.sqrt(bar['n'])) # 6 sigma

ax.bar(range(N), yvalues, yerr=yerr, facecolor='#777777', align='center', ecolor='black')
ax.set_ylabel('avg bw per node in mbps')
ax.set_xlabel('# node pairs')
ax.set_xticks(range(N))
ax.set_title(sys.argv[1])
ax.set_xticklabels(xlabels)
outfile = '%s.png' % fname
plt.savefig(outfile)
print 'saved to %s' % (outfile)
