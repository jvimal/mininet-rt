#!/usr/bin/python

"""
"""

import re

#convert bandwidth string to float and normalize it to Mbit/sec
def getBandwidth(bwStr):
  bw = bwStr.strip().split(',')[-1]
  return float(bw)/1e6

