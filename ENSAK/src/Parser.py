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
    '''statement : ila_stmt
            | men_stmt
            | lkola_stmt
            | mahed_stmt
            | htal_stmt
            | expression_stmt
    '''
    p[0] = p[1]
    
# Definition of "ILA_STMT"
def p_ila_stmt(p):
    '''ila_stmt : ILA expression block'''
    p[0] = AST.IfElseNode(p[2], p[3])
    
def p_ila_stmt_makantch(p):
    '''ila_stmt : ILA expression block MAKANTCH block'''
    p[0] = AST.IfElseNode(p[2], p[3], p[5])
    
def p_ila_stmt_makantchila(p):
    '''ila_stmt : ILA expression block MAKANTCH ila_stmt'''
    p[0] = AST.IfElseNode(p[2], p[3], p[5])
    
# Definition of "MEN_STMT"
def p_men_stmt(p):
    '''men_stmt : MEN expression ',' expression ',' expression block'''
    p[0] = AST.ForNode(p[2], p[4], p[6], p[7])
   
# Definition of "LKOLA_STMT"
def p_lkola_stmt(p):
    '''lkola_stmt : id '[' nl statement_list ']' '''
    p[0] = AST.ForEachNode(p[1], p[4])
    
# Definition of "WHILE_STMT"
def p_mahed_stmt(p):
    '''mahed_stmt : MAHED expression block'''
    p[0] = AST.WhileNode(p[2], p[3])
    
# Definition of "UNTIL_STMT"
def p_htal_stmt(p):
    '''htal_stmt : HTAL expression block'''
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
    
def p_expression_s7i7(p):
    'expression : S7I7'
    p[0] = AST.TokenNode(True)
    
def p_expression_KHAT2A(p):
    'expression : KHAT2A'
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
            print ("Khata2 f l fichier: maymkench n9raw had le fichier! '%s'!" % sys.argv[1])
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
        print ("Khata2 f les arguments: Khassek t 7eded fichier f l'argument lewel!")
        exit(-1)
else:
    import AST as AST