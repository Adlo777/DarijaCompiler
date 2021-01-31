#!/usr/bin/python
# -*- coding: latin-1 -*-

# External imports
from __future__ import with_statement
import ply.yacc as yacc

# Project imports
from LexAnalyser import tokens

# Definition of class YaccAnalysisError
class YaccAnalysisError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
        
    def __repr__(self):
        return "YaccAnalysisError(%s, %d)" % (self.message, self.line)
        
    def __str__(self):
        return "%s in line %d" % (self.message, self.line)
        
# Definition of "PROGRAM"
def p_program(p):
    '''program : statement_list'''
    p[0] = p[1]
    
def p_program_nl(p):
    '''program : nl statement_list'''
    p[0] = p[2]
    
# Definition of "STATEMENT_LIST"
def p_statement_list(p):
    '''statement_list : statement
            | statement nl'''
    p[0] = AST.ProgramNode([p[1]])
    
def p_statement_list_recursive(p):
    '''statement_list : statement nl statement_list'''
    p[0] = AST.ProgramNode([p[1]] + p[3].children)
    
# Definition of "STATEMENT"
def p_statement(p):
    '''statement : if_stmt
            | for_stmt
            | foreach_stmt
            | while_stmt
            | until_stmt
            | expression_stmt'''
    p[0] = p[1]
    
# Definition of "IF_STMT"
def p_if_stmt(p):
    '''if_stmt : IF expression block'''
    p[0] = AST.IfElseNode(p[2], p[3])
    
def p_if_stmt_else(p):
    '''if_stmt : IF expression block ELSE block'''
    p[0] = AST.IfElseNode(p[2], p[3], p[5])
    
def p_if_stmt_elseif(p):
    '''if_stmt : IF expression block ELSE if_stmt'''
    p[0] = AST.IfElseNode(p[2], p[3], p[5])
    
# Definition of "FOR_STMT"
def p_for_stmt(p):
    '''for_stmt : FOR expression ',' expression ',' expression block'''
    p[0] = AST.ForNode(p[2], p[4], p[6], p[7])
    
# Definition of "FOREACH_STMT"
def p_foreach_stmt(p):
    '''foreach_stmt : id '[' nl statement_list ']' '''
    p[0] = AST.ForEachNode(p[1], p[4])
    
# Definition of "WHILE_STMT"
def p_while_stmt(p):
    '''while_stmt : WHILE expression block'''
    p[0] = AST.WhileNode(p[2], p[3])
    
# Definition of "UNTIL_STMT"
def p_until_stmt(p):
    '''until_stmt : UNTIL expression block'''
    p[0] = AST.UntilNode(p[2], p[3])
    
# Definition of "EXPRESSION_STMT"
def p_expression_stmt(p):
    '''expression_stmt : expression '''
    p[0] = p[1]
    
# Definition of "BLOCK"
def p_block(p):
    '''block : '{' nl statement_list '}' '''
    p[0] = p[3]
    
# Definition of "NL"
def p_nl(p):
    '''nl : NEWLINE'''
    pass
    
def p_nl_recursive(p):
    '''nl : nl NEWLINE'''
    pass
    
# Definition of "EXPRESSION"
def p_expression_unary(p):
    '''expression : expression OP_UNARY'''
    p[0] = AST.OpNode(p[2], p[1])

def p_expression_not(p):
    '''expression : '!' expression'''
    p[0] = AST.OpNode(p[1], p[2])
    
def p_expression_mul(p):
    '''expression : expression OP_MUL expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_add(p):
    '''expression : expression OP_ADD expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_rela(p):
    '''expression : expression OP_RELA expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_comp(p):
    '''expression : expression OP_COMP expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_and(p):
    '''expression : expression AND_LOGIC expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_or(p):
    '''expression : expression OR_LOGIC expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])
    
def p_expression_assign(p):
    '''expression : expression OP_ASSIGN expression'''
    p[0] = AST.OpNode(p[2], p[1], p[3])

def p_expression_bracket(p):
    ''' expression : '(' expression ')' '''
    p[0] = p[2]
    
def p_expression_num(p):
    'expression : NUMBER'
    p[0] = AST.TokenNode(p[1])
    
def p_expression_true(p):
    'expression : TRUE'
    p[0] = AST.TokenNode(True)
    
def p_expression_false(p):
    'expression : FALSE'
    p[0] = AST.TokenNode(False)
    
def p_expression_identifier(p):
    '''expression : id'''
    p[0] = p[1]
    
def p_expression_call(p):
    '''expression : call'''
    p[0] = p[1]
    
# Definition of "ID"
def p_identifier(p):
    '''id : IDENTIFIER'''
    p[0] = AST.IdentifierNode(AST.TokenNode(p[1]))
    
def p_identifier_recursive(p):
    '''id : IDENTIFIER '.' id'''
    p[0] = AST.IdentifierNode(AST.TokenNode(p[1]), p[3])
    
# Definition of "CALL"
def p_call(p):
    '''call : id '(' ')' '''
    p[0] = AST.CallNode(p[1])
    
def p_call_parameters(p):
    '''call : id '(' parameters ')' '''
    p[0] = AST.CallNode(p[1], p[3].children)
    
# Definition of "PARAMETERS"
def p_parameters(p):
    '''parameters : expression'''
    p[0] = AST.ProgramNode([p[1]])
    
def p_parameters_recursive(p):
    '''parameters : expression ',' parameters'''
    p[0] = AST.ProgramNode([p[1]] + p[3].children)
    
# Catch error
def p_error(p):
    raise YaccAnalysisError("Syntax error", p.lineno)
    
# Definition of precedences
precedence = (
    ('right', 'OP_ASSIGN'),
    ('left', 'OR_LOGIC'),
    ('left', 'AND_LOGIC'),
    ('left', 'OP_COMP'),
    ('left', 'OP_RELA'),
    ('left', 'OP_ADD'),
    ('left', 'OP_MUL'),
    ('left', 'OP_UNARY'),
    ('left', '!'),
    ('left', '.')
)

# Construct YACC
yacc.yacc(outputdir='generated')

def parse(program):
    return yacc.parse(program)
    
if __name__ == "__main__":
    import sys, os
    
    if len(sys.argv) == 2:
        # File open
        try:
            file = open(os.path.normpath(os.path.normcase(sys.argv[1])), 'r')
        except IOError:
            print ("File error: Can't open the file '%s' in read mode!" % sys.argv[1])
            exit(-1)
            
        import ASTDraw as AST
    	
    	# Read file using a context manager
        with file:
            prog = file.read()
            try:
                result = yacc.parse(prog)
            except :
                print ("Error")
                exit(-1)
                
            graph = result.makegraphicaltree()
            name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
            graph.write_pdf(name)
            
            print (result)
            print ("AST was written to", name)
    else:
        print ("Arguments error: Please specify a file as first argument!")
        exit(-1)
else:
    import AST as AST