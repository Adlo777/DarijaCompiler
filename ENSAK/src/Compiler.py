#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
    Compiler of the program. The last part of all
    the process.

    Anthony Mougin <anthony.mougin@he-arc.ch>
    LANCO 2008-2009
'''

import time
import AST
from AST import addToClass
from Message import *
import Lex as vsllex
import Parser as vslparse
from Operations import *

#####################################
#         INITIALISATION            #
#####################################

# Initialisation of the compilation
def init():
    global compilerror      # Compiler error
    global currentscope     # The current scope under compilation (for error checking)
    global currentfunction  # The current function under compilation (for error checking)
    global ifcount          # If counter (for label)
    global whilecount       # While counter (for label)
    global forcount         # For counter (for label)

    currentscope = []
    currentfunction = None
    ifcount = 0
    forcount = 0
    whilecount = 0
    compilerror = 0

#####################################
#             PROGRAM               #
#####################################

@addToClass(vslcomp_ast.ProgramNode)
def compile(self):
    global functionPop
    functionPop=False
    result = ""
    # Compile all the elements of the program
    for element in self.elements:
        if element != None:
            if isinstance(element,vslcomp_ast.FunctionCallNode): functionPop=True
            result += element.compile()
    return result


#####################################
#             FUNCTIONS             #
#####################################

@addToClass(vslcomp_ast.FunctionCallNode)
def compile(self):
    global functionPop
    result = ""
    # Compile all the param of the calling
    for param in self.params:
        result += param.compile()
    # Call the method
    result += "CALL "+self.name+" "+str(len(self.params))+"\n"
    # If the method don't return anything, pop the top of stack (don't need the default return param)
    if not [f for f in vslparse.functiondef if f.name==self.name][0].isReturn or functionPop: result += 'POP\n'
    functionPop=False
    return result

@addToClass(vslcomp_ast.FunctionDefNode)
def compile(self):
    # If the method is unused, then do not compile them (Optimisation)
    if not self.unused:
        global currentscope
        global currentfunction
        # Set the current function under compilation
        currentfunction = self
        # Get all the local param of the function (not param and not global)
        local = [v for v in self.variables if not v.isGlobal and v.name not in self.params]

        # Set the label of function
        result = self.name+': '
        # If they are local variable, allocate the memory
        if len(local)>0: result += 'ALLOC '+str(len(local))+'\n'
        # If there is a program in the function
        if self.program != None: result += self.program.compile()
        # If the function return something
        if self.ret != None: result += self.ret.expression.compile()
        else:   result += 'PUSHI 0\n' # Else return a default value
        # If the function is the main function, EXIT the program with the code
        if self.name=='main': result += 'EXIT\n'
        else: result += 'RETURN '+str(len(local))+'\n' # Else return the value
        currentscope = [] # Ré-initialize the current scope
        return result
    return ''

@addToClass(vslcomp_ast.SpecFuncNode)
def compile(self):
    result = ""
    # Compile the params
    for param in self.params:
        result += param.compile()
    # Use the name of the function for the name of the op code
    result += self.func+'\n'
    return result

@addToClass(vslcomp_ast.CastNode)
def compile(self):
    return self.data.compile()+self.to+'\n'

#####################################
#        ELEMENT OF PROGRAM         #
#####################################

@addToClass(vslcomp_ast.VariableNode)
def compile(self):
    return getCorrectScope('GET',self)

@addToClass(vslcomp_ast.TokenNode)
def compile(self):
    result = ""
    # Use the correct push for the token
    if isinstance(self.tok, float):
        result = "PUSHF "+str(self.tok)+"\n"
    elif isinstance(self.tok, int):
        result = "PUSHI "+str(self.tok)+"\n"
    elif isinstance(self.tok, str):
        result = "PUSHS "+self.tok+"\n"
    return result

#####################################
#        LOOPS COMPILATION          #
#####################################

@addToClass(vslcomp_ast.WhileNode)
def compile(self):
    global whilecount
    # Get the current while number and save it
    current = whilecount
    whilecount+=1
    cmd = ''
    # If it is a DO-WHILE, don't jump now to the condition evaluation,
    # execute program first
    if not self.isDo:
        cmd  = "JMP whilecond"+str(current)+"\n"
    cmd += "whilebody"+str(current)+": "+self.program.compile()
    cmd += "whilecond"+str(current)+": "+self.condition.compile()
    cmd += "JNZ whilebody"+str(current)+"\n"
    return cmd

@addToClass(vslcomp_ast.ForNode)
def compile(self):
    global forcount
    # Get the current for number and save it
    current = forcount
    forcount+=1
    cmd  = ""
    # Compile all the initialisation
    for f in self.forcondition.initialisation:  cmd += f.compile()
    # Jump directly to the condition
    cmd += "JMP forcond"+str(current)+"\n"
    # Program of the while
    cmd += 'forbody'+str(current)+': '+self.program.compile()
    # Compile all the action to do before the program
    for f in self.forcondition.action: cmd += f.compile()
    # If there is condition, compile it, else push always to true
    if self.forcondition.condition != None: cond = self.forcondition.condition.compile()
    else: cond = 'PUSHI 1\n'
    cmd += 'forcond'+str(current)+': '+cond
    cmd += "JNZ forbody"+str(current)+"\n"
    return cmd

#####################################
#          IF STRUCTURE             #
#####################################

@addToClass(vslcomp_ast.IfNode)
def compile(self):
    global ifcount
    # Get the current if number and save it
    current = ifcount
    ifcount+=1
    # If seperation (between elif etc...)
    ifsepcount = 0
    
    # IF COMPILATION
    ifresult = self.condition.compile()
    # If there is no elif and no else, then go to the end of if
    # Else go to the first separation
    if len(self.eliflist)==0 and self.elsestruct == None: ifresult += 'JZ endif'+str(current)+'\n'
    else: ifresult += 'JZ ifsep'+str(current)+'_'+str(ifsepcount)+'\n'
    # Compile the if program
    ifresult += self.program.compile()
    # If they are elif and no else, jump to the end of if.
    if len(self.eliflist)!=0 or self.elsestruct != None:
        ifresult += 'JMP endif'+str(current)+'\n'

    # ELIF COMPILATION
    # Compile all the elif
    for num,el in enumerate(self.eliflist):
        # Add a separator
        ifresult += 'ifsep'+str(current)+'_'+str(ifsepcount)+': '
        # Compil the current elif condition
        ifresult += el.condition.compile()
        # If the are an other elif next or the are a else, jump to the next separator
        # If the condition is not good. Else jump to the end
        if num != len(self.eliflist)-1 or self.elsestruct != None:
            ifresult += 'JZ ifsep'+str(current)+'_'+str(ifsepcount+1)+'\n'
        else:
            ifresult += 'JZ endif'+str(current)+'\n'
        # Compile the elif program
        ifresult += el.program.compile()
        # If the are another struct next, add the jump to the end of if structure
        if num != len(self.eliflist)-1 or self.elsestruct != None:
            ifresult += 'JMP endif'+str(current)+'\n'
        # Increment the number of if separator
        ifsepcount += 1

    # ELSE COMPILATION
    # If there is an else
    if self.elsestruct != None:
        # Add the separator
        ifresult += 'ifsep'+str(current)+'_'+str(ifsepcount)+': '
        # Compile the else program
        ifresult += self.elsestruct.program.compile()

    # The end of the if structure
    ifresult += 'endif'+str(current)+': '
    return ifresult

#####################################
#          ARRAY ELEMENTS           #
#####################################

@addToClass(vslcomp_ast.CreateArrayNode)
def compile(self):
    return 'CREATEARRAY\n'

@addToClass(vslcomp_ast.ArrayElementNode)
def compile(self):
    # If it's an acces element
    if self.access: result = self.name.compile()+self.indice.compile()+'GET\n'
    else: # If it's an assignement
        result = self.name.compile()+self.indice.compile()
        # Assign the compile expression
        result += self.expression.compile()+'SET\n'
    return result

#####################################
#           STANDARD IO             #
#####################################

@addToClass(vslcomp_ast.PrintNode)
def compile(self):
    return self.expression.compile()+"WRITE\n"

@addToClass(vslcomp_ast.PrintlnNode)
def compile(self):
    return 'PUSHS ""\nWRITE\n'

@addToClass(vslcomp_ast.ReadNode)
def compile(self):
    return "READ\n"

#####################################
#        ELEMENTS OPERATIONS        #
#####################################

@addToClass(vslcomp_ast.OpNode)
def compile(self):
    # Test for check error with illegal strings operations
    testStringOperation(self.op,self.children,self.line)

    if self.op in operations and len(self.children) > 1:
        return operations[self.op](self.children[0].compile(),self.children[1].compile())   # Double operations
    elif self.op in unary_operations:
        return unary_operations[self.op](self.children[0].compile())        # Unary operations
    elif self.op in unary_op_assign:
        return unary_op_assign[self.op](self.children[0].compile(),getCorrectScope('SET',self.children[0]))       # Unary operations
    elif self.op in operations_assign:
        return operations_assign[self.op](self.children[0].compile(),self.children[1].compile(),getCorrectScope('SET',self.children[0])) # Here is the operations with assignement (+=, -= ....)

@addToClass(vslcomp_ast.AssignNode)
def compile(self):
    return self.expression.compile()+getCorrectScope('SET',self.identifier)

#####################################
#          EMPTY ELEMENT            #
#####################################

@addToClass(vslcomp_ast.EmptyNode)
def compile(self):
    return ''   # Don't do anything

#####################################
#       UTILITIES FUNCTIONS         #
#####################################

# Get the correct command ((GET/SET)G, (GET/SET)L or (GET/SET)P)
def getCorrectScope(typ,param):
    global currentfunction
    globalnames = [v.name for v in vslparse.globalvars] # List of globals name
    if currentfunction and param.name in currentfunction.params: return typ.upper()+'P '+str(currentfunction.params.index(param.name))+'\n' # If parameter of the function
    elif param.isGlobal: return typ.upper()+'G '+str(globalnames.index(param.name))+'\n' # If global of the program of the function
    else: return typ.upper()+'L '+str(getLocalIndex(param.name))+'\n' # If local of the function

# Get the local index of the given variable
# The virtual machine work with index
def getLocalIndex(var):
    '''Get the local index of a variable'''
    if var not in currentscope:
        currentscope.append(var)    # If it is the first time we have this variable, push it in the currentscope
    return currentscope.index(var)  # Get the index of the variable

#####################################
#          TEST FUNCTIONS           #
#####################################

# Test if the operation is correct (STRING only accept '+')
def testStringOperation(op,children,line):
    '''Test if if the operation is correct'''
    string = False  # Found a string
    number = False  # Found a number
    for c in children:
        if isinstance(c,vslcomp_ast.TokenNode): # For all the operand
            global compilerror
            if isinstance(c.tok,str):   
                string = True   # Found str
                if op not in ['+','!=','==']:   # If we use a invalid operation for string
                    error("Compilation error: can not use the operation '"+op+"' with string object",line)
                    compilerror+=1
            if isinstance(c.tok,int) or isinstance(c.tok,float): number = True  # Found number
    # Found string and number in the same operation, and the operation is not multi
    if string and number and op != '*':
        error("Compilation error: can not use the operation '"+op+"' between string and number",line)
        compilerror+=1

#####################################
#         MAIN COMPILATION          #
#####################################

# Compile a document
def compile(doc):
    '''Compile the given document'''
    from vslcomp_parser import parse
    import sys, os

    print 'Compilation of '+doc+'...'

    # Begin timing
    t = time.time()
    # Init the compilation
    init()
    # Read the file
    prog = file(doc).read()
    # Parse the document
    result = parse(prog,doc)
    # If the result is an AST Node (parsing success)
    if isinstance(result,vslcomp_ast.Node):
        compiled = ""
        for imp in vslparse.importlist:
            compiled += imp.compile()
        # Compile the AST node
        compiled += result.compile()

        # If success
        if not compilerror:
            globalloc = ""
            # Allocate the program globals
            if len(vslparse.globalvars):  globalloc += 'ALLOC '+str(len(vslparse.globalvars))+'\n'
            # Add the global allocation, the loading of programs arguments and the calling
            # main method at the begining of the bite code
            compiled = globalloc+'GETPROGARGS\nCALL main 1\n'+compiled
            success('Compilation',doc,vslparse.warningfound,time.time()-t)
            return compiled
        else:
            failed('Compilation',doc,compilerror)
            return COMPILE_ERROR_CODE
    else: 
        failed('Compilation',doc,vsllex.lexicalerror+vslparse.parserror)
        return result

# The main function are only here for debug. The real compiler don't need this
if __name__ == '__main__':
    import sys, os
    global compilerror

    if len(sys.argv)>1 and (not os.path.exists('bin') or not os.path.isdir('bin')): os.mkdir('bin')
    elif len(sys.argv)<2 or sys.argv[1]=='*.vsl': print ' * Nothing to compil'

    try:
        for i in range(1,len(sys.argv)):
            if os.path.exists(sys.argv[i]): compile(sys.argv[i])
    except (KeyboardInterrupt, SystemExit):
        pass
