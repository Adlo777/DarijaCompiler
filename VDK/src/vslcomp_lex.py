#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
    Operations op code. Needed by the vslcomp_compiler.py

    Anthony Mougin <anthony.mougin@he-arc.ch>
    LANCO 2008-2009
'''

import ply.lex as lex
from vslcomp_message import *

########################
#    Reserved object   #
########################

# Reserved constant name
reserved_const = (
    'TRUE',
    'FALSE',
    'PI',
    'NULL'
)

# Reserved function name
reserved_func = (
    'COS',
    'SIN',
    'TAN',
    'ARCCOS',
    'ARCSIN',
    'ARCTAN',
    'ABS',
    'EXP',
    'LOG',
    'SQRT',
    'OPEN',
    'CLOSE',
    'PRINT',
    'WRITEFILE',
    'PRINTLN',
    'READ',
    'READFILE',
    'STR',
    'FLOAT',
    'INT',
    'ISARRAY',
    'ISINT',
    'ISFLOAT',
    'ISSTR',
    'LEN',
    'SPLIT',
    'APPEND',
    'GET',
    'SET',
    'INSERT',
    'REMOVE'
)

# Reserved word of the code
reserved_words = (
    'IF',
    'ELSE',
    'ELIF',
    'DO',
    'WHILE',
    'FOR',
    'GLOBAL',
    'RETURN',
    'FUNCTION',
    'IMPORT',
)

# The specific tokens of our code
tokens = (
    'STRING',
    'NUMBER',
    'IDENTIFIER',
    'DOUBLE_OP',
    'UNARY_OP',
    'EQUAL',
    'ADD_OP',
    'OTHER_OP',
    'COMP_OP',
    'LOG_OP',
    'SEMICOLON',
    'COMMA',
    'PAR_OPEN',
    'PAR_CLOSE',
    'BRA_OPEN',
    'BRA_CLOSE',
    'CR_OPEN',
    'CR_CLOSE',
) + tuple(map(lambda s:s.upper(),reserved_words+reserved_func+reserved_const))

#########################
# Definitions of tokens #
#########################

def t_SIMPLE_COMMENTS(t):
    r'//.*'

def t_BLOCK_COMMENTS(t):
    r'/\*(\n|.)*?(\*/)'
    t.value=t.value.count('\n')*'\n'
    t_newline(t)

def t_STRING(t):
    r'".*?"'
    return t

def t_NUMBER(t):
    r'\d*\.?\d+'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    #r'[a−zA−Z_]\w∗'
    if t.value.upper() in (reserved_func+reserved_words+reserved_const):
        t.type = t.value.upper()
    return t

def t_DOUBLE_OP(t):
    r'\+= | -= | \*= | /='
    return t

def t_UNARY_OP(t):
    r'\+\+ | --'
    return t

def t_ADD_OP(t):
    r'[\+-]'
    return t

def t_OTHER_OP(t):
    r'\*\* | \* | / | %'
    return t

def t_COMP_OP(t):
    r'!= | <= | >= | == | [<>]'
    return t

def t_EQUAL(t):
    r'='
    return t

def t_LOG_OP(t):
    r'&& | \|\| | ! | \^'
    return t

def t_SEMICOLON(t):
    r';'
    return t

def t_COMMA(t):
    r','
    return t

def t_PAR_OPEN(t):
    r'\('
    return t

def t_PAR_CLOSE(t):
    r'\)'
    return t

def t_BRA_OPEN(t):
    r'{'
    return t

def t_BRA_CLOSE(t):
    r'}'
    return t

def t_CR_OPEN(t):
    r'\['
    return t

def t_CR_CLOSE(t):
    r'\]'
    return t

# When a new line
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore tab and empty space
t_ignore = ' \t'

# Error manager
def t_error(t):
    global lexicalerror
    lexicalerror+=1
    error("Illegal character '%s'" % t.value[0],t.lineno)
    t.lexer.skip(1)

def initLex():
    'Initialize lex'
    global lex
    global lexicalerror

    # The number of error found
    lexicalerror=0
    lex.lex()

# The main function are only here for debug. The real compiler don't need this3
if __name__ == '__main__':
    import sys
    for i in range(1,len(sys.argv)):
        if sys.argv[i]!='-v':
            prog = file(sys.argv[i]).read()
            print ("Lexical analysis of file"+sys.argv[i])
            initLex()
            lex.input(prog)
            while 1:
                tok = lex.token()
                if not tok: break
                if '-v' in sys.argv:
                    print ("line %d: %s(%s)" % (tok.lineno, tok.type, tok.value))
            if lexicalerror:
                failed('Lexical analysis',sys.argv[i],lexicalerror)
                sys.exit(LEXICAL_ERROR_CODE)
            else:
                success("Lexical analysis",sys.argv[i],False)
            lexicalerror=0
    sys.exit(EXIT_SUCCESS)

