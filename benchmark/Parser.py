#!/usr/bin/python

"""
"""

import re

#convert bandwidth string to float and normalize it to Mbit/sec
def getBandwidth(bwStr):
    r = re.compile("(\d+(\.\d+)?) (\w+)/(\w+)")
    bw_re = r.search(bwStr)
    if bw_re is not None:
	bw = float(bw_re.group(1))
	bwUnit = bw_re.group(3)
	if(re.search("mb(it)?(?!yte)", bwUnit, re.I)):
	    bw = bw
	elif(re.search("gb(it)?(?!yte)", bwUnit, re.I)):
	    bw = bw*1000.0
	elif(re.search("kb(it)?(?!yte)", bwUnit, re.I)):
	    bw = bw/1000.0
	elif(re.search("mb(yte)?", bwUnit, re.I)):
	    bw = bw*8.0
	elif(re.search("gb(yte)?", bwUnit, re.I)):
	    bw = bw*8.0*1000.0
	elif(re.search("kb(yte)?", bwUnit, re.I)):
	    bw = bw*8.0/1000.0
	else:
	    bw = 0
	return bw

    return 0
