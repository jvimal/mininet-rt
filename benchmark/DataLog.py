#!/usr/bin/python

"""
"""

import sys
flush = sys.stdout.flush

import csv
import re

class DataLog (object):
    "Module to log data in standard formats"

    f = None
    fname = ''
    fmt = None
    mode = None
    reader = None
    writer = None

    #set filename and format
    def __init__(self, filename=None, mode="r", fmt="csv"):
	if(filename is not None):
	    self.fname = filename
	self.fmt = fmt
	self.mode = mode
	print self.fname, self.mode, self.fmt

    #open file for writing
    def init(self):
	try:
	    self.f = open(self.fname, self.mode)
	    return True
	except IOError:
	    print "Could not open", self.fname, "in", self.mode, "mode."
	    return False

    #check if there is an open file handle
    def hasOpenFile(self):
	if((self.f is not None) and (not self.f.closed)):
	    return True
	return False

    #set the mode in which the file is opened
    def setMode(self, mode):
	if(not self.hasOpenFile()):
	    self.mode = mode
	    return True
	return False

    #get the mode in which the file is opened
    def getMode(self):
	return self.mode

    #set the file format
    def setFormat(self, fmt):
	if(not self.hasOpenFile()):
	    self.fmt = fmt
	    return True
	return False

    #get the file format
    def getFormat(self):
	return self.fmt

    #close any open files
    def close(self):
	if(self.hasOpenFile()):
	    self.f.close()

    #set file
    def setFile(self, filename, closeExisting=False):
	if(closeExisting):
	    self.close()
	else:
	    if(self.hasOpenFile()):
		return False
	self.fname = filename
	return True

    #read a list from the input file
    def readList(self):
	if(not self.hasOpenFile()):
	    print "Error: No open file."
	    return None

	r = re.compile("r")
	if(r.search(self.mode) is None):
	    print "Error: The file not opened in read mode."
	    return None

	if(self.fmt == "csv"):
	    if(self.reader is None):
		self.reader = csv.reader(f)
	    try:
		row = self.reader.next()
		return row
	    except StopIteration:
		return None

	return None
	
    #log a list in the output file
    def logList(self, l):
	r = re.compile("w|a|\+")
	if(r.search(self.mode) is None):
	    print "Error: The file not opened in write mode."
	    return False

	if(not self.hasOpenFile()):
	    return False

	if(self.fmt == "csv"):
	    if(self.writer is None):
		self.writer = csv.writer(self.f)

	    self.writer.writerow(l)
	    return True

	return False

