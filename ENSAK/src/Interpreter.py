#!/usr/bin/python
# -*- coding: latin-1 -*-

# External imports
from __future__ import with_statement

# Project imports
from Parser import parse

def interpret(code):
    result = parse(code)
    result.run()
    
if __name__ == "__main__":
    import sys, os
    
    if len(sys.argv) == 2:
        # File open
        try:
            file = open(os.path.normpath(os.path.normcase(sys.argv[1])), 'r')
        except IOError:
            print ("File error: Can't open the file '%s' in read mode!" % sys.argv[1])
            exit(-1)
            
    	# Read file using a context manager
        with file:
            prog = file.read()
            try:
                interpret(prog)
            except 'ERROR TYPE HERE' as e:
                print(str(e))
                
                
    else:
        print ( "Arguments error: Please specify a file as first argument!")
        exit(-1)