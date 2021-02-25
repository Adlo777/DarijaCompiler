#!/usr/bin/python
# -*- coding: latin-1 -*-

# Project imports
from Monde import World, Collection, InterpreterError

world = World()
currentStack = [world]

# ******************************************************************************
# Node (unspecified)
# ******************************************************************************
class Node:
    pass
    
# ******************************************************************************
# ProgramNode
# ******************************************************************************
class ProgramNode(Node):
    def __init__(self, children):
        self.children = children
        
    def run(self):
        for child in self.children:
            child.run()
            
# ******************************************************************************
# IfElseNode
# ******************************************************************************
class IfElseNode(Node):
    def __init__(self, cond, if_block, else_block = None):
        self.cond = cond
        self.if_block = if_block
        self.else_block = else_block
        
    def run(self):
        if self.cond.run():
            self.if_block.run()
        elif self.else_block:
                self.else_block.run()
                
# ******************************************************************************
# ForNode
# ******************************************************************************
class ForNode(Node):
    def __init__(self, init, cond, step, block):
        self.init = init
        self.cond = cond
        self.step = step
        self.block = block
        
    def run(self):
        self.init.run()
        while self.cond.run():
            self.block.run()
            self.step.run()
            
# ******************************************************************************
# ForEachNode
# ******************************************************************************
class ForEachNode(Node):
    def __init__(self, id, block):
        self.id = id
        self.block = block
        
    def run(self):
        global currentStack
        collection = self.id.run()
        # Verify that this id is a collection
        try:
            iter(collection)
        except:
            raise InterpreterError("kayn khata2 f la boucle:machi collection '%s' " % collection)
        for item in collection:
            currentStack.append(item)
            self.block.run()
            currentStack.pop() 
            
# ******************************************************************************
# WhileNode
# ******************************************************************************
class WhileNode(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
        
    def run(self):
        while self.cond.run():
            self.block.run()
            
            
            
# ******************************************************************************
# PrintNode
# ******************************************************************************
class PrintNode(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
        
    def run(self):
        while self.cond.run():
            self.block.run()
                        
# ******************************************************************************
# UntilNode
# ******************************************************************************
class UntilNode(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block
        
    def run(self):
        while not self.cond.run():
            self.block.run()
            
# ******************************************************************************
# OpNode
# ******************************************************************************
class OpNode(Node):
    def __init__(self, op, left = None, right = None):
        self.op = op
        self.left = left
        self.right = right
        
    def run(self):
        if self.op == '==':
            return self.left.run() == self.right.run()
        elif self.op == '!=':
            return self.left.run() != self.right.run()
        elif self.op == '&&':
            return self.left.run() and self.right.run()
        elif self.op == '||':
            return self.left.run() or self.right.run()
        elif self.op == '=':
            return self.left.assign(self.right.run())
        elif self.op == '!':
            return not self.left.run()
        else:
            leftValue = self.__autoCast(self.left.run())
            if self.right:
                rightValue = self.__autoCast(self.right.run())
            else:
                rightValue = None
            if type(leftValue) == float:
                return self.__processNumber(leftValue, rightValue)
            else:
                if isinstance(leftValue, Collection):
                    return self.__processList(leftValue, rightValue)
                else:
                    return self.__processObject(leftValue, rightValue)
                    
    def __processObject(self, leftValue, rightValue):
        if type(rightValue) == float:
            raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad 7a9i9i." % self.op)
        else:
            if isinstance(rightValue, Collection):
                if self.op == '+' or self.op == '+=':
                    rightValue.add(leftValue)
                    return rightValue
                elif self.op == '-' or self.op == '-=':
                    rightValue.remove(leftValue)
                    return rightValue
                else:
                    raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad list." % self.op)
            else:
                if self.op == '+':
                    return Collection([leftValue, rightValue])
                else:
                    raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object ." % self.op)
                    
    def __processNumber(self, leftValue, rightValue):
        if rightValue and type(rightValue) != float:
            raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad 7a9i9i." % self.op)
        else:
            if self.op == '*':
                return leftValue * rightValue
            elif self.op == '/':
                try:
                    return leftValue / rightValue
                except:
                    raise InterpreterError("Had l'operation khat2a: 9issma 3la zero.")
            elif self.op == '%':
                try:
                    return leftValue % rightValue
                except:
                    raise InterpreterError("Had l'operation khat2a:9issma 3la zero.")#Operation error Dision /0
            elif self.op == '+':
                return leftValue + rightValue
            elif self.op == '-':
                return leftValue - rightValue
            elif self.op == '<':
                return leftValue < rightValue
            elif self.op == '<=':
                return leftValue <= rightValue
            elif self.op == '>':
                return leftValue > rightValue
            elif self.op == '>=':
                return leftValue >= rightValue
            elif self.op == '*=':
                return self.left.assign(leftValue * rightValue)
            elif self.op == '/=':
                try:
                    return self.left.assign(leftValue / rightValue)
                except:
                    raise InterpreterError("Had l'operation khat2a:9issma 3la zero.")
            elif self.op == '%=':
                try:
                    return self.left.assign(leftValue % rightValue)
                except:
                    raise InterpreterError("Had l'operation khat2a:lba9i zero..")
            elif self.op == '+=':
                return self.left.assign(leftValue + rightValue)
            elif self.op == '-=':
                return self.left.assign(leftValue - rightValue)
            elif self.op == '++':
                return self.left.assign(leftValue + 1)
            elif self.op == '--':
                return self.left.assign(leftValue - 1)
            else:
                raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad 7a9i9i." % self.op)
                
    def __processList(self, leftValue, rightValue):
        if type(rightValue) == float:
            raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad list." % self.op)
        else:
            if isinstance(rightValue, Collection):
                if self.op == '+' or self.op == '+=':
                    leftValue.addList(rightValue)
                    return leftValue
                elif self.op == '-' or self.op == '-=':
                    leftValue.removeList(rightValue)
                    return leftValue
                else:
                    raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou lists." % self.op)
            else:
                if self.op == '+':
                    leftValue.add(rightValue)
                    return leftValue
                else:
                    raise InterpreterError("Had l'operation khat2a: '%s maymkench nderou object m3a 3adad list."  % self.op)
                    
    def __autoCast(self, value):
        if type(value) == bool:
            return float(value)
        if type(value) == int:
            return float(value)
        return value
        
# ******************************************************************************
# CallNode
# ******************************************************************************
class CallNode(Node):
    def __init__(self, id, params = None):
        self.id = id
        self.params = params
        
    def run(self):
        function = self.id.run()
        if callable(function):
            p = []
            if self.params:
                for param in self.params:
                    # Can raise exceptions, but they are allowed to go
                    p.append(param.run())
            try:
                return function(*p)
            except 'kayn khata2 f Interpretation' as e:
                raise e
            except 'Kayn khata2 f Exception' as e:
                raise e
                raise InterpreterError("kayn khata2 f la fonction." % str(function))
        else:
            # This id doesn't return a callable function
            raise InterpreterError("kayn khata2 f la fonction." % str(function))
            
# ******************************************************************************
# IdentifierNode
# ******************************************************************************
class IdentifierNode(Node):
    def __init__(self, id, subids = None):
        self.id = id
        self.subids = subids
        
    def run(self, root = None):
        global world
        global currentStack
        idValue = self.id.run()
        if root:
            path = root
        else:
            if idValue == 'current':
                if self.subids:
                    return self.subids.run(currentStack[-1])
                else:
                    return currentStack[-1]
            path = world
        if hasattr(path, idValue):
            if self.subids:
                return self.subids.run(getattr(path, idValue))
            else:
                return getattr(path, idValue)
        else:
            if self.subids:
                # If toto doesn't exist, cannot search for toto.titi.
                raise InterpreterError("Identification khat2a : makaynach." % idValue)
            else:
                # Assume that this identifier will be assigned later
                return None
                
    def assign(self, value, root = None):
        global world
        global currentStack
        idValue = self.id.run()
        if root:
            path = root
        else:
            if idValue == 'current':
                if self.subids:
                    return self.subids.assign(value, currentStack[-1])
                else:
                    # Current cannot be changed because it's managed automatically for 'foreach' loops.
                    raise InterpreterError("Assignment khat2a : '%s' maymkench n7ededouh ." % idValue)
            path = world
        if hasattr(path, idValue):
            if self.subids:
                return self.subids.assign(value, getattr(path, idValue))
            else:
                setattr(path, idValue, value)
                return getattr(path, idValue)
        else:
            if self.subids:
                # If toto doesn't exist, cannot assign toto.titi.
                raise InterpreterError("Assignment khat2a : '%s' maymkench n7ededouh ." % idValue)
            else:
                setattr(path, idValue, value)
                return getattr(path, idValue)
                
# ******************************************************************************
# TokenNode
# ******************************************************************************
class TokenNode(Node):
    def __init__(self, token):
        self.token = token
        
    def run(self):
        return self.token
        
    def assign(self, value, root = None):
        raise InterpreterError("Assignment khat2a : '%s' machi variable." % self.token)