#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
    Operations op code. Needed by the vslcomp_compiler.py

    Anthony Mougin <anthony.mougin@he-arc.ch>
    LANCO 2008-2009
'''

operations = {
    '+' : lambda x,y: x+y+'ADD\n',
    '-' : lambda x,y: x+y+'SUB\n',
    '*' : lambda x,y: x+y+'MUL\n',
    '/' : lambda x,y: x+y+'DIV\n',
    '**' : lambda x,y: x+y+'POW\n',
    '%' : lambda x,y: x+y+'MOD\n',
    '<'  : lambda x,y: x+y+'LT\n',
    '>'  : lambda x,y: x+y+'GT\n',
    '==' : lambda x,y: x+y+'EQ\n',
    '!=' : lambda x,y: x+y+'NE\n',
    '<=' : lambda x,y: x+y+'LE\n',
    '>=' : lambda x,y: x+y+'GE\n',
    '&&' : lambda x,y: x+y+'AND\n',
    '||' : lambda x,y: x+y+'OR\n',
    '^' : lambda x,y: x+y+'XOR\n'
}

operations_assign = {
    '+=' : lambda x,y,assign: operations['+'](x,y)+assign,
    '-=' : lambda x,y,assign: operations['-'](x,y)+assign,
    '*=' : lambda x,y,assign: operations['*'](x,y)+assign,
    '/=' : lambda x,y,assign: operations['/'](x,y)+assign
}

unary_operations = {
    '-' : lambda x: x+'NEG\n',
    '!'  : lambda x: x+'NOT\n'
}

unary_op_assign = {
    '++': lambda x,assign: x+'INC\n'+assign,
    '--': lambda x,assign: x+'DEC\n'+assign
}

