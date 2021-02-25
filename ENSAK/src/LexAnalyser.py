#!/usr/bin/python
# -*- coding: latin-1 -*-

# External imports
from __future__ import with_statement
import ply.lex as lex

# Definition of class LexAnalysisError
class LexAnalysisError(Exception):
    def __init__(self, message, line, value):
        self.message = message
        self.line = line
        self.value = value
        
    def __repr__(self):
        return "LexAnalysisError(%s, %d, %s)" % (self.message, self.line, self.value)
        
    def __str__(self):
        return "%s at line %d (value %s)" % (self.message, self.line, self.value)
        
# List of reserved words
reserved_words = (
    'ila',#si
    'makantch',#sinon
    'men',#for
    'mahed',#while
    'htal',#until
    'lkola',#foreach
    's7i7',
    'khat2a',#false
)

# List of tokens
tokens = (
    'OP_UNARY',     # ++ --
    'OP_MUL',       # * / %
    'OP_ADD',       # + -
    'OP_RELA',      # < <= > >=
    'OP_COMP',      # == !=
    'AND_LOGIC',    # &&
    'OR_LOGIC',     # ||
    'OP_ASSIGN',    # = += -= *= /= %=
    'NUMBER',       # int / float / exponential
    'IDENTIFIER',
    'NEWLINE'
) + tuple(map(lambda s:s.upper(), reserved_words))

# List of litterals (token of one character)
literals = '.(){},![]'

# Definition of the token "OP_COMP"
# Support operators : == !=
def t_OP_COMP(t):
    r'[=!]='
    return t
    
# Definition of the token "OP_ASSIGN"
# Support operators : = *= /= += -= %=
def t_OP_ASSIGN(t):
    r'[*/+%-]?='
    return t
    
# Definition of the token "NUMBER"
# Support formats : int / float / exponential
def t_NUMBER(t):
    r'-?\d+(\.\d*)?(e-?\d+)?'
    try:
        t.value = float(t.value)   
        print (t.value)
    except ValueError:
        raise LexAnalysisError("Exception while parsing number" , t.lineno, t.value) #Erreur de parsing
    return t
    
# Definition of the token "OP_UNARY"
# Support operators : ++ --
def t_OP_UNARY(t):
    r'(\+\+)|(\-\-)'
    return t
    
# Definition of the token "OP_MUL"
# Support operators : * / %
def t_OP_MUL(t):
    r'[*/%]'
    return t
    
# Definition of the token "OP_ADD"
# Support operators : + -
def t_OP_ADD(t):
    r'[+-]'
    return t
    
# Definition of the token "OP_RELA"
# Support operators : < <= > >=
def t_OP_RELA(t):
    r'[<>]=?'
    return t
    
# Definition of the token "AND_LOGIC"
# Support operators : &&
def t_AND_LOGIC(t):
    r'&&'
    return t
    
# Definition of the token "OR_LOGIC"
# Support operators : ||
def t_OR_LOGIC(t):
    r'\|\|'
    return t
    
# Definition of the token "COMMENT"
# Support monoline comment : #
t_ignore_COMMENT = r'\#.*' # Comments are ignored

# Definition of the token "IDENTIFIER"
# Check for reserved word
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in reserved_words:
        t.type = t.value.upper()
        t.value = ''
    return t
    
# Definition of the token "NEWLINE"
def t_NEWLINE(t):
    r'[\n\r]+'
    t.lexer.lineno += len(t.value.strip('\r'))
    t.value = ''
    return t
    
# Ignore white spaces
t_ignore  = ' \t'

# Catch error
def t_error(t):
    raise LexAnalysisError("Had l 7erf khate2", t.lineno, repr(t.value[0]))#illegal character
    
# Construct LEX
lexer = lex.lex()

# If the file is not used as a module
if __name__ == "__main__":
    import sys, os
    
    if len(sys.argv) == 2:
        # File open
        try:
            file = open(os.path.normpath(os.path.normcase(sys.argv[1])), 'r')
        except IOError:
            print ("Khata2 f l fichier: maymkench n9raw had le fichier!" % sys.argv[1])#File error: can't open this file in read mode 
            exit(-1)
    	    
    	# Read file using a context manager
        with file:
            prog = file.read()
            lexer.input(prog)
            
            while 1:
                    tok = lexer.token()
              
    else:
        print ("Khata2 f les arguments: Khassek t 7eded fichier f l'argument lewel!")#Arguments error: please specify a file as first argument
        exit(-1)