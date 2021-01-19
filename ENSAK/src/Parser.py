#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
    Parser of the program (yacc part of PLY)
'''

import ply.lex as lex
import Lex as vsllex
from Lex import tokens
import ply.yacc as yacc
from message import *
from AST import *

# Initialyse 
def init():
    '''Initialize global variable and lex'''
    global parserror            # number of parsing error
    global globalvars           # list of global variable
    global function             # list of call function
    global functiondef          # list of delared function
    global currentscope         # The currentscope (for test)
    global importlist           # The import list of file
    global allReadyImport       # The already import absolute path file
    global currentpath          # The current path of parsing (for import)

    parserror=0
    globalvars = []
    function = []
    functiondef = []
    currentscope = []
    importlist = []
    allReadyImport = []
    currentpath = ''

    #Initialize the lexical analysis
    vsllex.initLex()

###        BEGIN OF GRAMMAR       ###

#####################################
#           MAIN PROGRAM            #
#####################################

# Main program statement complex
def p_mainprogram_statement_imp(p):
    '''mainprogram : importlist funclist'''
    p[0] = ProgramNode(p[2])

# Main program statement
def p_mainprogram_statement(p):
    '''mainprogram : funclist'''
    p[0] = ProgramNode(p[1])

#####################################
#         IMPORT PROGRAM            #
#####################################

# A import
def p_import(p):
    '''importlist : IMPORT STRING SEMICOLON'''
    from os.path import isabs
    global importlist
    global currentpath
    p[2] = p[2][1:len(p[2])-1]
    if not p[2].endswith('.vsl'): p[2] = p[2]+'.vsl'
    if not isabs(p[2]): p[2] = currentpath+p[2]
    importlist.append(p[2])

# A import recursive
def p_import_rec(p):
    '''importlist : IMPORT STRING SEMICOLON importlist'''
    from os.path import isabs
    global importlist
    global currentpath
    p[2] = p[2][1:len(p[2])-1]
    if not p[2].endswith('.vsl'): p[2] = p[2]+'.vsl'
    if not isabs(p[2]): p[2] = currentpath+p[2]
    importlist.append(p[2])

#####################################
#          NORMAL PROGRAM           #
#####################################

# Program statement
def p_program_statement(p):
    '''program : statement
        | block'''
    p[0] = ProgramNode([p[1]])

# Program recursive statement
def p_program_recursive(p):
    '''program : statement program
        | block program'''
    p[0] = ProgramNode([p[1]]+p[2].elements)

#####################################
#        FUNCTION DEFINITION        #
#####################################

# The function list
def p_funclist(p):
    '''funclist : functiondef'''
    p[0] = [p[1]]

# The recusrsive function list
def p_funclist_recursive(p):
    '''funclist : functiondef funclist'''
    p[0] = [p[1]]+p[2]

# A definition of a function with a return
def p_function_return_def(p):
    '''functiondef : FUNCTION IDENTIFIER PAR_OPEN identparam PAR_CLOSE functionblock'''
    global currentscope
    f = FunctionDefNode(p[2],p[4],p.lineno(1),True,currentscope,p[6][0],p[6][1])
    functiondef.append(f)
    currentscope=[]
    p[0] = f

# A definition of a function without return
def p_function_noreturn_def(p):
    '''functiondef : FUNCTION IDENTIFIER PAR_OPEN identparam PAR_CLOSE block'''
    global currentscope
    f = FunctionDefNode(p[2],p[4],p.lineno(1),False,currentscope,p[6])
    functiondef.append(f)
    currentscope=[]
    p[0] = f

#####################################
#   PARAM FOR FUNCTION DEFINITION   #
#####################################

# The empty identifier parameter
def p_identparam_empty(p):
    '''identparam : empty'''
    p[0] = []

# A simple identifier paramater
def p_identparam_simple(p):
    '''identparam : IDENTIFIER'''
    currentscope.append(VariableNode(p[1],p.lineno(1)))
    p[1] = testVarScope(p[1])
    p[0] = p[1]

# The identifier parameters recursive definition
def p_identparam_recursive(p):
    '''identparam : IDENTIFIER COMMA identparam'''
    currentscope.append(VariableNode(p[1],p.lineno(1)))
    p[1] = testVarScope(p[1])
    if not isinstance(p[3],list):
        p[0] = [p[1],p[3]]
    else:
        p[0] = [p[1]]+p[3]

#####################################
#          A FUNCTION CALL          #
#####################################

# A function call
def p_function(p):
    '''function : IDENTIFIER PAR_OPEN param PAR_CLOSE'''
    for param in p[3]:
        testVarScope(param);
    f = FunctionCallNode(p[1],p[3],p.lineno(1))
    function.append(f)
    p[0]=f

#####################################
#     PARAM OF CALLING FUNCTION     #
#####################################

# The empty parameter
def p_param_empty(p):
    '''param : empty'''
    p[0] = []

# A simple paramater
def p_param_simple(p):
    '''param : expression'''
    p[0] = [p[1]]

# The parameters recursive definition
def p_param_recursive(p):
    '''param : expression COMMA param'''
    if not isinstance(p[3],list):
        p[0] = [p[1],p[3]]
    else:
        p[0] = [p[1]]+p[3]

#####################################
#            STATEMENT              #
#####################################

# A simple statement
def p_simple_statement(p):
    '''statement : assignement SEMICOLON
            | doubleop SEMICOLON
            | unary SEMICOLON
            | structure
            | function SEMICOLON
            | globaldec'''
    p[0]=p[1]

#####################################
#         GLOBAL DECLARATION        #
#####################################

# A global statement definition
def p_global_declaration(p):
    '''globaldec : GLOBAL IDENTIFIER SEMICOLON'''
    if p[2] not in [g.name for g in globalvars]:
        var = VariableNode(p[2],p.lineno(2),True)
        globalvars.append(var)
    else:
        var = globalvars[[g.name for g in globalvars].index(p[2])]

    if p[2] not in [l.name for l in currentscope]:
        currentscope.append(var)
    else:
        global parserror
        error("Multiple definition of global "+str(p[2])+" in this scope",p.lineno(2))
        parserror+=1

#####################################
#      ASSIGNEMENT DECLARATION      #
#####################################

# A assignement (Ex: toto = 3)
def p_assignement(p):
    '''assignement : IDENTIFIER EQUAL expression
        | IDENTIFIER EQUAL newarray
        | array_element EQUAL expression'''
    p[3] = testVarScope(p[3])
    if isinstance(p[1],ArrayElementNode):
        p[1].access = False
        p[1].expression = p[3]
        p[0] = p[1]
    else:
        if p[1] not in [var.name for var in currentscope]:
            currentscope.append(VariableNode(p[1],p.lineno(1)))
        p[0] = AssignNode(VariableNode(p[1],p.lineno(1),p[1] in [f.name for f in globalvars]),p[3])

#####################################
#   WHILE, DO-WHILE AND FOR LOOP    #
#####################################

# A WHILE structure
def p_while_structure(p):
    '''structure : WHILE PAR_OPEN expression PAR_CLOSE block
        | WHILE PAR_OPEN expression PAR_CLOSE statement'''
    p[0] = WhileNode(p[3],p[5])

# A DO .... WHILE structure
def p_dowhile_structure(p):
    '''structure : DO block WHILE PAR_OPEN expression PAR_CLOSE
        | DO statement WHILE PAR_OPEN expression PAR_CLOSE'''
    p[0] = WhileNode(p[5],p[2],True)

# A FOR structure
def p_for_structure(p):
    '''structure : FOR PAR_OPEN forinit SEMICOLON forcondition SEMICOLON foraction PAR_CLOSE block
        | FOR PAR_OPEN forinit SEMICOLON forcondition SEMICOLON foraction PAR_CLOSE statement'''
    p[0] = ForNode(ForConditionNode(p[3],p[5],p[7]),p[9])

#####################################
#     FOR LOOP SPECIAL PARAMETER    #
#####################################

# For loop initialisation
def p_for_initialisation(p):
    '''forinit : assignement
        | empty'''
    p[0]=[p[1]]

# For loop initialisation recursive
def p_for_initialisation_rec(p):
    '''forinit : assignement COMMA forinit'''
    p[0]=[p[1]]+p[3]

# For loop condition
def p_for_condition(p):
    '''forcondition : expression 
        | empty'''
    p[0]=p[1]

# For loop action
def p_for_action(p):
    '''foraction : assignement
        | function
        | doubleop
        | unary
        | empty'''
    p[0]=[p[1]]

# For loop action recursive
def p_for_action_rec(p):
    '''foraction : assignement COMMA foraction
        | function COMMA foraction
        | doubleop COMMA foraction
        | unary COMMA foraction'''
    p[0]=[p[1]]+p[3]

#####################################
#     IF { ELIF } [ELSE] STRUCT     #
#####################################

# An simple IF structure
def p_if_structure(p):
    '''ifstructure : IF PAR_OPEN expression PAR_CLOSE block
        | IF PAR_OPEN expression PAR_CLOSE statement'''
    p[3] = testVarScope(p[3])
    p[0] = IfNode(p[3],p[5])

# The else element
def p_else_element(p):
    '''elsestruct : ELSE block
        | ELSE statement
        | empty'''
    if len(p)==3: p[0] = ElseNode(p[2])
    else: p[0] = None

# An if-else simple IF structure
def p_if_element_structure(p):
    '''structure : ifstructure eliflist elsestruct'''
    p[1].elsestruct = p[3]
    p[1].eliflist += p[2]
    p[0] = p[1]

# An if-else simple IF structure
def p_if_simple_structure(p):
    '''structure : ifstructure elsestruct'''
    p[1].elsestruct = p[2]
    p[0] = p[1]

# A elif structure
def p_simple_elif(p):
    '''elifstruct : ELIF PAR_OPEN expression PAR_CLOSE block
        | ELIF PAR_OPEN expression PAR_CLOSE statement'''
    p[0] = [ElifNode(p[3],p[5])]

# A elif list
def p_simple_elif_list(p):
    '''eliflist : elifstruct'''
    p[0] = p[1]

# The elif recursive list
def p_recursive_elif_list(p):
    '''eliflist : elifstruct eliflist'''
    p[0] = p[1]+p[2]

#####################################
#          BLOC OF PROGRAM          #
#####################################

# A block of program (separate by { and })
def p_block(p):
    '''block : BRA_OPEN program BRA_CLOSE
        | BRA_OPEN empty BRA_CLOSE'''
    p[0] = p[2]

#####################################
#        SPEC BLOC OF PROGRAM       #
#####################################

# A block with a ending return value (special for function)
def p_function_block(p):
    '''functionblock : BRA_OPEN program RETURN expression SEMICOLON BRA_CLOSE
        | BRA_OPEN empty RETURN expression SEMICOLON BRA_CLOSE'''
    p[4] = testVarScope(p[4])
    p[0] = [p[2],ReturnNode(p[4])]

#####################################
#        STANDARD IO FUNCTION       #
#####################################

# The print function
def p_print_function(p):
    '''function : PRINT PAR_OPEN expression PAR_CLOSE'''
    p[3] = testVarScope(p[3])
    p[0] = PrintNode(p[3])

# The read function (keyboard)
def p_read_function(p):
    '''function : READ PAR_OPEN PAR_CLOSE'''
    p[0] = ReadNode()

# The println function
def p_println_function(p):
    '''function : PRINTLN PAR_OPEN PAR_CLOSE'''
    p[0] = PrintlnNode()

#####################################
#          FILE IO FUNCTION         #
#####################################

# Write a file
def p_writefile_Function(p):
    '''function : WRITEFILE PAR_OPEN expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int) or isinstance(p[3].tok,str)):
        global compilerror
        error(p[1]+" can only have file object for the first parameters",p.lineno(1))
        parserror+=1
    p[3] = testVarScope(p[3])
    p[5] = testVarScope(p[5])
    p[0] = SpecFuncNode(p[1],[p[3],p[5]],p.lineno(1))

# The read file
def p_readfile_function(p):
    '''function : READFILE PAR_OPEN expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int) or isinstance(p[3].tok,str)):
        global compilerror
        error(p[1]+" can only have file object for the first parameters",p.lineno(1))
        parserror=parserror+1
    p[0] = SpecFuncNode(p[1],[p[3]],p.lineno(1));

# The open file
def p_openfile_function(p):
    '''function : OPEN PAR_OPEN expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int)):
        global compilerror
        error(p[1]+" can only have strings object for the parameters",p.lineno(1))
        parserror+=1
    if isinstance(p[5],TokenNode) and (isinstance(p[5].tok,int)):
        global compilerror
        error(p[1]+" can only have strings object for the parameters",p.lineno(1))
        parserror+=1
    p[0] = SpecFuncNode(p[1],[p[3],p[5]],p.lineno(1));

# The close file
def p_closefile_function(p):
    '''function : CLOSE PAR_OPEN expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int)):
        global compilerror
        error(p[1]+" can only have strings object for the parameters",p.lineno(1))
        parserror+=1
    p[0] = SpecFuncNode(p[1],[p[3]],p.lineno(1));

#####################################
#      CLASS FUNCTION BY TYPE       #
#####################################

# All the mathfunc function name
def p_mathfunc_name(p):
    '''mathfunc : LEN
        | COS
        | SIN
        | TAN
        | ARCCOS
        | ARCSIN
        | ARCTAN
        | ABS
        | LOG
        | SQRT
        | EXP'''
    p[0] = p[1].upper()

# All the test function name
def p_testfunc_name(p):
    '''testfunc : ISARRAY
        | ISINT
        | ISFLOAT
        | ISSTR'''
    p[0] = p[1].upper()

# String function with 2 args
def p_double_args_string_func_name(p):
    '''stringfunc : SPLIT'''
    p[0] = p[1].upper()

# Array function with 2 args (the second is an indice)
def p_indice_array_func_name(p):
    '''indicearrayfunc : GET
        | REMOVE'''
    p[0] = p[1].upper()

# Array function with 2 args
def p_double_args_array_func_name(p):
    '''arrayfunc : APPEND'''
    p[0] = p[1].upper()

# Array function with 3 args
def p_tree_args_array_func_name(p):
    '''treearrayfunc : SET
        | INSERT'''
    p[0] = p[1].upper()

# the cast method
def p_cast_func_name(p):
    '''castfunc : STR
        | INT
        | FLOAT'''
    p[0] = 'TO'+p[1][0].upper()

#####################################
#  SPECIAL FUNCTION (MATH,ARRAY...) #
#####################################

# The math function
def p_math_function(p):
    '''function : mathfunc PAR_OPEN expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and isinstance(p[3].tok,str):
        global compilerror
        error("Math function doesn't support string parameters",p.lineno(1))
        parserror+=1

    p[3] = testVarScope(p[3])
    p[0] = SpecFuncNode(p[1],[p[3]],p.lineno(1))

# The test function
def p_test_function(p):
    '''function : testfunc PAR_OPEN expression PAR_CLOSE'''
    p[3] = testVarScope(p[3])
    p[0] = SpecFuncNode(p[1],[p[3]],p.lineno(1))

# The double string function func
def p_double_string_function(p):
    '''function : stringfunc PAR_OPEN expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and isinstance(p[3].tok,int):
        global compilerror
        error("String function doesn't support integer in parameters "+str(1),p.lineno(1))
        parserror+=1

    if isinstance(p[5],TokenNode) and isinstance(p[5].tok,int):
        global compilerror
        error("String function doesn't support integer in parameters "+str(1),p.lineno(1))
        parserror+=1
    
    p[3] = testVarScope(p[3])
    p[5] = testVarScope(p[5])
    p[0] = SpecFuncNode(p[1],[p[3],p[5]],p.lineno(1))

# The array func
def p_array_function(p):
    '''function : arrayfunc PAR_OPEN expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int) or isinstance(p[3].tok,str)):
        global compilerror
        error(p[1]+" can only have array for the first parameters",p.lineno(1))
        parserror+=1
    p[3] = testVarScope(p[3])
    p[5] = testVarScope(p[5])
    p[0] = SpecFuncNode(p[1],[p[3],p[5]],p.lineno(1))

# The array func
def p_indice_args_function(p):
    '''function : indicearrayfunc PAR_OPEN expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int) or isinstance(p[3].tok,str)):
        global compilerror
        error(p[1]+" can only have array for the first parameters",p.lineno(1))
        parserror+=1

    if isinstance(p[5],TokenNode) and not isinstance(p[5].tok,int):
        global compilerror
        error("Indice in array must be an integer",p.lineno(1))
        parserror+=1
    p[3] = VariableNode(p[3],p.lineno(1),p[3] in [g.name for g in globalvars])
    p[3] = testVarScope(p[3])
    p[5] = testVarScope(p[5])
    p[0] = SpecFuncNode(p[1],[p[3],p[5]],p.lineno(1))

# The double args array func
def p_doubles_array_function(p):
    '''function : treearrayfunc PAR_OPEN expression COMMA expression COMMA expression PAR_CLOSE'''
    if isinstance(p[3],TokenNode) and (isinstance(p[3].tok,int) or isinstance(p[3].tok,str)):
        global compilerror
        error(p[1]+" can only have array for the first parameters",p.lineno(1))
        parserror+=1

    if isinstance(p[5],TokenNode) and not isinstance(p[5].tok,int):
        global compilerror
        error("Indice in array must be an integer",p.lineno(1))
        parserror+=1

    p[3] = VariableNode(p[3],p.lineno(1),p[3] in [g.name for g in globalvars])
    p[3] = testVarScope(p[3])
    p[5] = testVarScope(p[5])
    p[7] = testVarScope(p[7])
    p[0] = SpecFuncNode(p[1],[p[3],p[5],p[7]],p.lineno(1))

# The cast function
def p_cast_function(p):
    '''function : castfunc PAR_OPEN expression PAR_CLOSE'''
    p[3] = testVarScope(p[3])
    p[0] = CastNode(p[3],p[1])

#####################################
#            EXPRESSION             #
#####################################

# Simple expression
def p_expression(p):
    '''expression : NUMBER
        | function
        | IDENTIFIER
        | STRING
        | array_element'''
    isFunction(p[1])
    if isinstance(p[1],str) and p[1][0]!='"' and p[1][len(p[1])-1]!='"':
        p[0] = VariableNode(p[1],p.lineno(1),p[1] in [g.name for g in globalvars])
    elif not isinstance(p[1],FunctionNode) and not isinstance(p[1],ReservedFuncNode) and not isinstance(p[1],ArrayElementNode):
        p[0] = TokenNode(p[1])
    else:
        p[0] = p[1]

# An expression between ( and )
def p_par_expression(p):
    '''expression : PAR_OPEN expression PAR_CLOSE'''
    p[0] = p[2]

#####################################
#       EXPRESSION OPERATIONS       #
#####################################

# Operations expression (with double attribute)
def p_dop_expression(p):
    '''expression : expression ADD_OP expression
        | expression OTHER_OP expression
        | expression COMP_OP expression
        | expression LOG_OP expression'''
    p[1] = testVarScope(p[1])
    p[3] = testVarScope(p[3])
    p[0] = OpNode(p[2],[p[1],p[3]],p.lineno(2))

# The double operation (with assignation)
def p_double_op(p):
    '''doubleop : expression DOUBLE_OP expression'''
    p[1] = testVarScope(p[1])
    p[3] = testVarScope(p[3])
    p[0]=OpNode(p[2],[p[1],p[3]],p.lineno(2))

# The unary incrementation, decrementation
def p_uop_inc(p):
    '''unary : IDENTIFIER UNARY_OP'''
    p[1] = VariableNode(p[1],p.lineno(1),p[1] in [f.name for f in globalvars])
    p[1] = testVarScope(p[1])
    p[0] = OpNode(p[2],p[1],p.lineno(1));

# Operations expression (with unary operation)
def p_uop_expression(p):
    '''expression : ADD_OP expression %prec UNARY_OP
        | LOG_OP expression %prec UNARY_OP'''
    p[2] = testVarScope(p[2])
    p[0] = OpNode(p[1],p[2],p.lineno(1))

#####################################
#          ARRAY ELEMENT            #
#####################################

# New array
def p_newarray_expression(p):
    '''newarray : CR_OPEN CR_CLOSE'''
    p[0] = CreateArrayNode()

# New array
def p_arrayelement_expression(p):
    '''array_element : expression CR_OPEN expression CR_CLOSE'''
    if isinstance(p[1],TokenNode) and isinstance(p[1].tok,int):
        global compilerror
        error("Integer can not be subscriptable",p.lineno(1))
        parserror+=1

    if isinstance(p[3],TokenNode) and not isinstance(p[3].tok,int):
        global compilerror
        error("Array indice must be integer",p.lineno(1))
        parserror+=1

    p[0] = ArrayElementNode(p[1],p[3])

#####################################
#             CONSTANTE             #
#####################################

# The True boolean expression
def p_true_expression(p):
    '''expression : TRUE'''
    p[0]=TokenNode(1)

# The False boolean expression
def p_false_expression(p):
    '''expression : FALSE'''
    p[0]=TokenNode(0)

# The NULL expression
def p_null_expression(p):
    '''expression : NULL'''
    p[0]=TokenNode(0)

# The PI expression
def p_pi_expression(p):
    '''expression : PI'''
    from math import pi
    p[0]=TokenNode(pi)

#####################################
#           EMPTY ELEMENT           #
#####################################

# Define an empty element
def p_empty(p):
    '''empty : '''
    p[0] = EmptyNode()

#####################################
#     PRECEDENCE (SHIFT/REDUCE)     #
#####################################

# The priority of operations
precedence = (
    ('left', 'LOG_OP'),
    ('left', 'COMP_OP'),
    ('left', 'ADD_OP'),
    ('left', 'OTHER_OP'),
    ('left', 'UNARY_OP'),
    ('left', 'CR_OPEN'),
    ('right', 'ELIF'),
    ('right', 'ELSE')
)

#####################################
#           ERROR DISPLAY           #
#####################################

# The error catcher
def p_error(p):
    '''The error catcher'''
    if p:
        global parserror
        parserror+=1
        error("Syntax error. %s is not attempt here." % p.type,p.lineno)
        yacc.errok()

#####################################
#           GENERATE YACC           #
#####################################

# Initialize the yacc, create the temp folder
import os
from tempfile import mkdtemp
yacc.yacc(outputdir=mkdtemp(),debug=0)


###         END OF GRAMMAR         ###

#####################################
#   OTHER FUNCTION USE FOR PARSING  #
#####################################

# test if the given is a function, then make it need return
def isFunction(p):
    '''Test if the given param is a function and set that it need return'''
    if isinstance(p,FunctionCallNode):
        p.isReturn = True

# Get the length of an object (difference between list and other type)
def getlength(obj):
    'Get the length of an object'
    if isinstance(obj,list):
        return len(obj)
    else:
        return 1

#####################################
#  TEST FUNCTIONS FOR ERROR CHECK   #
#####################################

# test for the variable in the scope (declared etc...)
def testVarScope(var):
    '''Test for the variable in the scope'''
    global parserror
    listname = [varinst.name for varinst in currentscope]
    if isinstance(var,VariableNode):
        if var.name in listname:
            found = currentscope[listname.index(var.name)]
            found.unused=False
            return found
        else:
            error("The local variable "+var.name+" is not assigned before use",var.line)
            parserror+=1
            return var
    else:
        return var

# Test of correct function definition
def testFunctionDef():
    '''Test of functions definition (multiple)'''
    global parserror
    definitions={}
    deferror=0
    for func in functiondef:
        if func.name in definitions.keys():
            definitions[func.name].append(func.line)
        else:
            definitions[func.name] = [func.line]

    for name in definitions.keys():
        if len(definitions[name])>1:
            error('Multiple definition of function '+str(name)+' at lines: '+str(definitions[name]),0)
            parserror+=1

    globalname = [v.name for v in globalvars]
    for funcdef in functiondef:
        for param in funcdef.params:
            if param in globalname:
                error('Param '+param+' for the function '+funcdef.name+' has the same name that a global.',funcdef.line)
                parserror+=1

# Test the function call in the program
def testFunctionCall():
    '''Test of functions call and definition'''
    global parserror
    defFunctions = [func.name for func in functiondef]
    functionerror=0

    if 'main' not in defFunctions:
        error('the main function can not be found. No entry point for this program',0)
        parserror+=1
    else:
        mainfunc = [func for func in functiondef if func.name=='main'][0]
        if len(mainfunc.params)!=1:
            error('the main function can only have one arguments',mainfunc.line)
            parserror+=1

    for func in function:
        if func.name not in defFunctions:
            error('the function %s is not defined' % func.name,func.line)
            parserror+=1
        else:
            defFunction = functiondef[defFunctions.index(func.name)]
            if len(func.params) != len(defFunction.params):
                error('the function '+func.name+' take at most '+str(defFunction.nbparams)+' argument(s), but '+str(func.nbparams)+' given',func.line)
                parserror+=1
            
            if func.isReturn == True and defFunction.isReturn == False:
                error('the function '+func.name+' return no value',func.line)
                parserror+=1

# Test of unused function
def testUnusedFuncDeclaration():
    '''Test of unused function'''
    global warningfound
    call = [func.name for func in function]
    definition = [func.name for func in functiondef if func.name not in call]
    for d in definition:
        if d != 'main':
            func = [f for f in functiondef if f.name==d][0]
            warning('unused function '+str(d),func.line)
            func.unused=True
            warningfound+=1

# Test of unused variable and global in each scope
def testUnusedVarDeclaration():
    '''Test of unused variables and globals declarations'''
    global warningfound
    for d in functiondef:
        if d.name != 'main':
            d.variables.reverse()
            for var in d.variables:
                if var.unused and not var.isGlobal:
                    warning('unused local variable '+str(var.name),var.line)
                    warningfound+=1

    for g in globalvars:
        if g.unused:
            warning('unused global '+str(g.name),g.line)
            warningfound+=1

# Delete the main function definition in an AST
def deleteMainFunc(AST):
    '''Delete the main function definition in an AST'''
    mainFunc = [f for f in AST.elements if f.name == 'main']
    if len(mainFunc):
        AST.elements.remove(mainFunc[0])
        functiondef.remove(mainFunc[0])
    return AST

###############################################
#    THE YACC PARSE WITH PARSING OF IMPORT    #
###############################################

# Parse program (recursive)
def parseImport(program,level=0):
    from os.path import abspath
    global importlist
    global allReadyImport
    global currentpath

    # Parse the program
    result = yacc.parse(program)

    # Parse the import list
    for n,imp in enumerate(importlist[level:]):
        vsllex.initLex()
        if not isinstance(imp,Node):
            if os.path.exists(imp):
                currentpath = getAllPath(imp)
                if abspath(imp) not in allReadyImport:
                    allReadyImport.append(abspath(imp))
                    AST = parseImport(file(imp).read(),level+1)
                    importlist[n+level] = deleteMainFunc(AST)
                else: 
                    print('Already compile')
                    importlist.remove(imp)
            else:
                warning('Import '+imp+' not found.',0);
                importlist.remove(imp)
    return result

def getAllPath(f):
    from os.path import abspath
    return abspath(f)[:len(os.path.abspath(f))-len(os.path.basename(f))]

###############################################
#  THE MAIN METHOD TO PARSE A GIVEN PROGRAM   #
###############################################

# Parse a given program
def parse(program,name):
    '''Parse a program'''
    from os.path import abspath
    global parserror
    global warningfound
    global importlist
    global allReadyImport
    global currentpath
    
    # Init the parser (and the lexer)
    init()
    currentpath = getAllPath(name)
    allReadyImport.append(abspath(name))
    result = parseImport(program)
    errorCode=0
    # If lexical error found
    if vsllex.lexicalerror: errorCode+=LEXICAL_ERROR_CODE

    # Check error
    testFunctionDef()
    testFunctionCall()
    # Check warning
    global warningfound
    warningfound=0
    testUnusedFuncDeclaration()
    testUnusedVarDeclaration()

    # If parsing error found
    if parserror: errorCode+=PARSING_ERROR_CODE

    # Check if error found (yacc or/and lex)
    if errorCode: return errorCode
    else: return result

# !! The main function are only here for debug. The real compiler don't need this`!!
if __name__ == '__main__':
    import sys
    global warningfound
    for i in range(1,len(sys.argv)):
        prog = file(sys.argv[i]).read()
        print ("Parsing "+sys.argv[i]+"...")

        AST = parse(prog,sys.argv[i])
        if isinstance(AST,Node):
            success('Parsing',sys.argv[i],warningfound)
            print (AST)
        else: sys.exit(AST)
    sys.exit(EXIT_SUCCESS)
