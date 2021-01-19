#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
    Parser of the program (yacc part of PLY)

    Anthony Mougin <anthony.mougin@he-arc.ch>
    LANCO 2008-2009
'''

EXIT_SUCCESS = 0        # Exit succes
LEXICAL_ERROR_CODE = 1    # the lexical analyse error exit code
PARSING_ERROR_CODE = 2    # the parsing error exit code
COMPILE_ERROR_CODE = 4    # the compilation error exit code
NOTHING_COMPILE_ERROR_CODE = 8    # Nothing to compil
# Error code can be cumulate

# Display error with line
def error(message, line):
    '''Display an error'''
    print ("  ** Error line %d: %s" % (line,message))

# Display warning with line
def warning(message, line, filename=""):
    '''Display a warning'''
    print ("  * Warning line %d: %s" % (line,message))

# Display the success of an operation
def success(operation,filename,warning=False,period=None):
    '''Display the success of an operation on a file'''
    message = "  * "+str(operation)+" of "+str(filename)+" done"
    if period: message += ' in %.4f secs' % (period)
    if warning: message += " with warnings"
    else: message+="."
    print (message)

# Display the failor of an operation
def failed(operation,filename,nberror):
    '''Display the failure of an operation on a file'''
    print ('  ** '+str(operation)+' of '+str(filename)+' failed because of '+str(nberror)+' error(s)')
