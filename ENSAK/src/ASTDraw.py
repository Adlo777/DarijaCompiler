#!/usr/bin/python
# -*- coding: latin-1 -*-

# External imports
import pydot

# ******************************************************************************
# Node (unspecified)
# ******************************************************************************
class Node:
    count = 0
    type = 'Node (unspecified)'
    shape = 'ellipse'
    
    def __init__(self, children=None):
        self.ID = str(Node.count)
        Node.count += 1
        if not children:
            self.children = []
        elif hasattr(children,'__len__'):
            self.children = children
        else:
            self.children = [children]
        self.next = []
        
    def asciitree(self, prefix=''):
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if not isinstance(c,Node):
                result += "%s*** Error: Child of type %r: %r\n" % (prefix,type(c),c)
                continue
            result += c.asciitree(prefix)
        return result
        
    def __str__(self):
        return self.asciitree()
        
    def __repr__(self):
        return self.type
        
    def makegraphicaltree(self, dot=None, edgeLabels=True):
            if not dot:
                dot = pydot.Dot()
            dot.add_node(pydot.Node(self.ID, label=repr(self), shape=self.shape))
            label = edgeLabels and len(self.children)-1
            for i, c in enumerate(self.children):
                c.makegraphicaltree(dot, edgeLabels)
                edge = pydot.Edge(self.ID,c.ID)
                if label:
                    edge.set_label(str(i))
                dot.add_edge(edge)
                #Workaround for a bug in pydot 1.0.2 on Windows:
                dot.set_graphviz_executables({'dot': r'C:\Program Files\Graphviz2.16\bin\dot.exe'})
            return dot
            
# ******************************************************************************
# ProgramNode
# ******************************************************************************
class ProgramNode(Node):
    type = 'Program'
    
    def __init__(self, children):
        Node.__init__(self, children)
        
# ******************************************************************************
# IfElseNode
# ******************************************************************************
class IfElseNode(Node):
   type = 'IfElse'
   
   def __init__(self, cond, if_block, else_block = None):
        if else_block:
            Node.__init__(self, [cond, if_block, else_block])
        else:
            Node.__init__(self, [cond, if_block])
            
# ******************************************************************************
# ForNode
# ******************************************************************************
class ForNode(Node):
    type = 'For'
    
    def __init__(self, init, cond, step, block):
        Node.__init__(self, [init, cond, step, block])
        
# ******************************************************************************
# ForEachNode
# ******************************************************************************
class ForEachNode(Node):
    type = 'ForEach'
    
    def __init__(self, id, block):
        Node.__init__(self, [id, block])
        
# ******************************************************************************
# WhileNode
# ******************************************************************************
class WhileNode(Node):
    type = 'While'
    
    def __init__(self, cond, block):
        Node.__init__(self, [cond, block])
        
# ******************************************************************************
# UntilNode
# ******************************************************************************
class UntilNode(Node):
    type = 'Until'
    
    def __init__(self, cond, block):
        Node.__init__(self, [cond, block])
        
# ******************************************************************************
# OpNode
# ******************************************************************************
class OpNode(Node):
    type = 'Op'
    
    def __init__(self, op, left = None, right = None):
        children = []
        if left:
            children.append(left)
        if right:
            children.append(right)
        Node.__init__(self, children)
        self.op = op
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1
            
    def __repr__(self):
        return "%s (%s)" % (self.op, self.nbargs)
        
# ******************************************************************************
# CallNode
# ******************************************************************************
class CallNode(Node):
    type = 'Call'
    
    def __init__(self, id, params = None):
        if params:
            Node.__init__(self, [id] + params)
        else:
            Node.__init__(self, [id])
            
# ******************************************************************************
# IdentifierNode
# ******************************************************************************
class IdentifierNode(Node):
    type = 'Identifier'
    
    def __init__(self, id, subid = None):
        if subid:
            Node.__init__(self, [id] + [subid])
        else:
            Node.__init__(self, [id])
            
# ******************************************************************************
# TokenNode
# ******************************************************************************
class TokenNode(Node):
    type = 'Token'
    
    def __init__(self, tok):
        Node.__init__(self)
        self.tok = tok
        
    def __repr__(self):
        return repr(self.tok)