#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
  Darija Compiler Project 
  ECOLE NATIONALE DES SCIENCES APPLIQUEES
  WIAM-IBTISSAM-ADMEO
'''

#####################################
#             MAIN NODE             #
#####################################

# The main node class
class Node():
    count = 0
    type = 'Node (unspecified)'

    def __init__(self):
        self.count+=1

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.__dict__:
            if isinstance(c,Node):
                result += c.asciitree(prefix)
        return result

    def __str__(self):
        return self.asciitree()

    def __repr__(self):
        return self.type

#####################################
#   PROGRAM NODE (MAIN, FUNC, ...)  #
#####################################

# A program node
class ProgramNode(Node):
    '''The main program node'''
    type = 'program'
    def __init__(self,elements):
        '''The construcot of a main program'''
        Node.__init__(self)
        self.elements = elements

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element (for function)'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.elements:
            if isinstance(c,Node):
                result += c.asciitree(prefix)
        return result

#####################################
#             IMPORT                #
#####################################

# A import
class ImportNode(Node):
    '''The import node'''
    type='import'
    def __init__(self,name):
        Node.__init__(self)
        self.name = name

    def __repr__(self):
        return "%s: %s" % (self.type, self.name)

#####################################
#          FUNCTIONS NODE           #
#####################################

# The global function class
class FunctionNode(Node):
    '''The function (name, line, numbers of param, have or need return, unused, list of in-use variable)'''
    def __init__(self,name,params,line,isReturn=False,variables=[]):
        '''The constructor of a function'''
        if not isinstance(params,list):
            params = [params]
        Node.__init__(self)
        self.name = name
        self.params = params
        self.line = line
        self.isReturn = isReturn
        self.unused = False
        self.variables = variables

    def __repr__(self):
        return "%s: %s" % (self.type, self.name)

# The call function
class FunctionCallNode(FunctionNode):
    type='function_call'

# The definition of function
class FunctionDefNode(FunctionNode):
    type='function_def'
    def __init__(self,name,params,line,isReturn=False,variables=[],program=None,ret=None):
        Node.__init__(self)
        FunctionNode.__init__(self,name,params,line,isReturn,variables)
        self.program = program
        self.ret = ret

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element (for function)'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix)
        if isinstance(self.ret,Node):
            result += self.ret.asciitree(prefix)
        return result

# A return node of a function definition
class ReturnNode(Node):
    type='return'
    def __init__(self,expression):
        Node.__init__(self)
        self.expression = expression

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.expression,Node):
            result += self.expression.asciitree(prefix)
        return result

# The reserved Func main class (use for parser error check)
class ReservedFuncNode(Node):
    type='reservedfunc'
    def __init__(self,line=0):
        self.line = line
        Node.__init__(self)

#####################################
#       SPECIAL FUNCTIONS NODE      #
#####################################

# The array specific func
class SpecFuncNode(ReservedFuncNode):
    def __init__(self,func,params,line):
        ReservedFuncNode.__init__(self,line)
        type = func.lower()
        self.func = func
        self.params = params

# Casting node
class CastNode(ReservedFuncNode):
    type='cast'
    def __init__(self, data, to):
        ReservedFuncNode.__init__(self)
        self.data = data
        self.to = to

    def __repr__(self):
        return "%s (%s)" % (self.type, self.to)

#####################################
#     STANDARD IO FUNCTIONS NODE    #
#####################################

# A print node
class PrintNode(ReservedFuncNode):
    type='print'
    def __init__(self,expression):
        ReservedFuncNode.__init__(self)
        self.expression = expression

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.expression,Node):
            result += self.expression.asciitree(prefix)
        return result

# Print new line node
class PrintlnNode(ReservedFuncNode):
    type='println'

# A read node
class ReadNode(ReservedFuncNode):
    type='read'

#####################################
#           LOOPS NODE              #
#####################################

# While node
class WhileNode(Node):
    type='while'
    def __init__(self,condition,program,isDo=False):
        Node.__init__(self)
        self.condition = condition
        self.program = program
        self.isDo = isDo

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.condition,Node):
            result += self.condition.asciitree(prefix)
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix)
        return result

# A for node
class ForNode(Node):
    type='for'
    def __init__(self,forcondition,program):
        Node.__init__(self)
        self.forcondition = forcondition
        self.program = program

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.forcondition,Node):
            result += self.forcondition.asciitree(prefix)
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix)
        return result

# For condition node
class ForConditionNode(Node):
    type='forcondition'
    def __init__(self,initialisation,condition,action):
        Node.__init__(self)
        self.initialisation = initialisation
        self.condition = condition
        self.action = action

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.initialisation,Node):
            result += self.initialisation.asciitree(prefix)
        if isinstance(self.condition,Node):
            result += self.condition.asciitree(prefix)
        if isinstance(self.action,Node):
            result += self.action.asciitree(prefix)
        return result

#####################################
#       IF STRUCTURE NODE           #
#####################################

# The IF node
class IfNode(Node):
    type='if'
    def __init__(self,condition,program):
        Node.__init__(self)
        self.condition = condition
        self.program = program
        self.eliflist = []
        self.elsestruct = None

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix2 = prefix+'|  '
        if isinstance(self.condition,Node):
            result += self.condition.asciitree(prefix2)
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix2)
        for c in self.eliflist:
            if isinstance(c,Node):
                result += c.asciitree(prefix)
        if isinstance(self.elsestruct,Node):
            result += self.elsestruct.asciitree(prefix)
        return result

# The else part of the if node
class ElseNode(Node):
    type='else'
    def __init__(self,program):
        Node.__init__(self)
        self.program = program

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix)
        return result

# The elif part of the if node
class ElifNode(Node):
    type='elif'
    def __init__(self,condition,program):
        Node.__init__(self)
        self.condition = condition
        self.program = program

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.condition,Node):
            result += self.condition.asciitree(prefix)
        if isinstance(self.program,Node):
            result += self.program.asciitree(prefix)
        return result

#####################################
#         ARRAY ELEMENT NODE        #
#####################################

# Array constructor node
class CreateArrayNode(Node):
    type='new_array'

# Array element (ex: p[2])
class ArrayElementNode(Node):
    type='array_access'
    def __init__(self,name,indice,access=True,expression=None):
        self.name = name
        self.indice = indice
        self.access = access
        self.expression = expression

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.name,Node):
            result += self.name.asciitree(prefix)
        if isinstance(self.indice,Node):
            result += self.indice.asciitree(prefix)
        return result

#####################################
#      EXPRESSIONS OPERATIONS       #
#####################################

# A assign node
class AssignNode(Node):
    type='assignement'
    def __init__(self,identifier,expression):
        Node.__init__(self)
        self.identifier = identifier
        self.expression = expression

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        if isinstance(self.identifier,Node):
            result += self.identifier.asciitree(prefix)
        if isinstance(self.expression,Node):
            result += self.expression.asciitree(prefix)
        return result

# Operation node
class OpNode(Node):
    type='operation'
    def __init__(self, op, children, line):
        Node.__init__(self)
        if not isinstance(children, list): children = [children]
        self.children = children
        self.op = op
        self.line = line

    def asciitree(self, prefix=''):
        '''Display an ascii tree of element'''
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if isinstance(c,Node):
                result += c.asciitree(prefix)
        return result
        
    def __repr__(self):
        return "%s (%s)" % (self.op, len(self.children))

#####################################
#         PROGRAM ELEMENTS          #
#####################################

# A variable in the program
class VariableNode(Node):
    '''A variable in the program (name, unused, global or not)'''
    def __init__(self,name,line,isGlobal=False):
        Node.__init__(self)
        '''The constructor of a variable'''
        if isGlobal: self.type='global'
        else: self.type='local'
        self.name = name
        self.line = line
        self.isGlobal = isGlobal
        self.unused = True

    def __repr__(self):
        return "%s: %s" % (self.type, self.name)

# Token like number or string
class TokenNode(Node):
    '''A token in the program'''
    def __init__(self,tok):
        Node.__init__(self)
        self.tok = tok

    def __repr__(self):
        return repr(self.tok)

#####################################
#           EMPTY ELEMENT           #
#####################################

# Empty node (use for compilation)
class EmptyNode(Node):
    type='empty'

#####################################
#         ADD CLASS METHOD          #
#####################################

# To add a method to a given class (take from TP)
def addToClass(cls):
    ''' Décorateur permettant d'ajouter la fonction décorée en tant que méthode
    à une classe.
    
    Permet d'implémenter une forme élémentaire de programmation orientée
    aspects en regroupant les méthodes de différentes classes implémentant
    une même fonctionnalité en un seul endroit.
    
    Attention, après utilisation de ce décorateur, la fonction décorée reste dans
    le namespace courant. Si cela dérange, on peut utiliser del pour la détruire.
    Je ne sais pas s'il existe un moyen d'éviter ce phénomène.

    Référence: AST.py v0.2, 2008-2009, Matthieu Amiguet, HE-Arc
    '''
    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator
