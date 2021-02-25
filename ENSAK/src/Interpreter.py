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
            print ("Khata2 f l fichier: maymkench n9raw had le fichier!" % sys.argv[1])
            exit(-1)
            
    	# Read file using a context manager
        with file:
            prog = file.read()
            try:
                interpret(prog)
            except 'ERROR TYPE HERE' as e:
                print(str(e))
                
                
    else:
        print ( "Khata2 f les arguments: Khassek t 7eded fichier f l'argument lewel!")
        exit(-1)