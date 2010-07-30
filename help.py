import sys

def printhelp():
  print """Usage (as root): python %s [opts]
  opts:

    -n number
      Number of hosts, default 10

    -t time
      Amount of time to run, default 10

    -r rate
      Shape links to constant rate, default 100mbit

    -o file
      Output from tests get written to file
      default: results-$n-$t.html

    -d
      Start the hosts, configure the network and exit

    --dryrun
      Just print the commands

    --test
      Which test to run; 
        Default: none
        Available: iperf

    --stop
      Stop the containers and bring down the network

    -h,--help
      Print this help

    --tcpdump
      Run tcpdump on all hosts (not available now)

    --cpulimit x%%
      Limit each host to x%% of the CPU
        Default: no limit, just that all hosts have equal priority
""" % (sys.argv[0])

