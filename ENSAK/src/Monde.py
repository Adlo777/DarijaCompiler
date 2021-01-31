#!/usr/bin/python
# -*- coding: latin-1 -*-

# External imports
from random import random, randint
from math import ceil, floor
from time import sleep, time
import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE

# Definition of class InterpreterError
class InterpreterError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return "InterpreterError(%s)" % (self.message)
        
    def __str__(self):
        return "%s" % (self.message)
        
# ******************************************************************************
# Class Collection
# ******************************************************************************
class Collection:
    def __init__(self, initial = None):
        if initial:
            self.__list = initial
        else:
            self.__list = []
            
    def add(self, item):
        self.__list.append(item)
        
    def remove(self, item):
        self.__list.remove(item)
        
    def addList(self, another):
        for item in another:
            if item not in self.__list:
                self.add(item)
                
    def removeList(self, another):
        for item in another:
            self.remove(item)
            
    def forward(self):
        for item in self.__list:
            item.forward()
            
    def backward(self):
        for item in self.__list:
            item.backward()
            
    def turn(self, delta):
        for item in self.__list:
            item.turn(delta)
            
    def count(self):
        return len(self.__list)
        
    def __str__(self):
        return str(self.__list)
        
    def __iter__(self):
        return iter(self.__list)
        
    def __getattr__(self, name):
        if name == 'cars':
            coll = Collection()
            for item in self.__list:
                if isinstance(item, Car):
                    coll.add(item)
            return coll
        elif name == 'trucks':
            coll = Collection()
            for item in self.__list:
                if isinstance(item, Truck):
                    coll.add(item)
            return coll
        elif name == 'all':
            coll = Collection()
            for item in self.__list:
                coll.add(item)
            return coll
        else:
            raise AttributeError()
            
# ******************************************************************************
# Class RGB
# ******************************************************************************
class RGB:
    def __init__(self, r, g, b):
        try:
            self.__r = int(r) % 256
            self.__g = int(g) % 256
            self.__b = int(b) % 256
        except:
            raise InterpreterError('The three parameters of rgb must be integers. Usage: rgb(r, g, b)')
            
    def getR(self):
        return self.__r
        
    def setR(self, r):
        try:
            self.__r = int(r) % 256
        except:
            raise InterpreterError('The parameter of setR must be an integer. Usage: setR(r)')
            
    def getG(self):
        return self.__g
        
    def setG(self, g):
        try:
            self.__g = int(g) % 256
        except:
            raise InterpreterError('The parameter of setG must be an integer. Usage: setG(g)')
            
    def getB(self):
        return self.__b
        
    def setB(self, b):
        try:
            self.__b = int(b) % 256
        except:
            raise InterpreterError('The parameter of setB must be an integer. Usage: setB(b)')
            
# ******************************************************************************
# Class World
# ******************************************************************************
class World:
    def __init__(self):
        self.__nbX = 10
        self.__nbY = 10
        self.__collection = Collection()
        self.__color = RGB(255, 255, 255)
        self.__simulator = Simulator(self.__nbX, self.__nbY)
        
    # **************************************************************************
    # Operations
    # **************************************************************************
    def init(self, nbX = None, nbY = None, color = None):
        # Set the number of position in X and Y direction
        try:
            if nbX:
                self.__nbX = int(nbX)
            if nbY:
                self.__nbY = int(nbY)
        except:
            raise InterpreterError('The two first parameters of init must be integers. Usage: init([nbX[, nbY[, color]]])')
        # Update the simulator
        if nbX or nbY:
            self.__simulator = Simulator(self.__nbX, self.__nbY)
        # Set the background color
        if color:
            if isinstance(color, RGB):
                self.__color = color
            else:
                raise InterpreterError('The third parameter of init must be a RGB object. Usage: init([nbX[, nbY[, color]]])')
                
    def getColor(self):
        return self.__color
        
    def setColor(self, color):
        if color:
            if isinstance(color, RGB):
                self.__color = color
            else:
                raise InterpreterError('The parameter of setColor must be a RGB object. Usage: setColor(color)')
                
    def getNbX(self):
        return self.__nbX
        
    def getNbY(self):
        return self.__nbY
        
    # **************************************************************************
    # Functions
    # **************************************************************************
    def rgb(self, r, g, b):
        return RGB(r, g, b)
        
    def truck(self, x = 0, y = 0, direction = 0):
        t = Truck(self, x, y, direction)
        self.__collection.add(t)
        return t
        
    def car(self, x = 0, y = 0, direction = 0):
        c = Car(self, x, y, direction)
        self.__collection.add(c)
        return c
        
    def rand(self, min = None, max = None):
        if min != None and max == None:
            raise InterpreterError("The two parameters of rand must be set or not but not only one. Usage: rand([min, max])")
        if min != None and max != None:
            try:
                min = int(min)
                max = int(max)
            except:
                raise InterpreterError("The two parameters of rand must be integers. Usage: rand([min, max])")
            return randint(min, max)
        else:
            return random()
            
    def ceil(self, nb):
        return ceil(nb)
        
    def floor(self, nb):
        return floor(nb)
        
    def paint(self, delay = 0.5):
        self.__simulator.paint(self, delay)
        
    def echo(self, what):
        print (str(what))
        
    # **************************************************************************
    # Getter
    # **************************************************************************
    def __getattr__(self, name):
        return getattr(self.__collection, name)
        
# ******************************************************************************
# Class World
# ******************************************************************************
class WorldObject:
    def __init__(self, world, x = 0, y = 0, direction = 0):
        try:
            self.__x = int(x)
            self.__y = int(y)
            # Direction logic :
            #   3    2    1
            #   4    X    0
            #   5    6    7
            self.__direction = int(direction) % 8
        except:
            raise InterpreterError('The three parameters of car and truck must be integers. Usage: car([x[, y[, direction]]])')
        self.__world = world
        
    def isCar(self):
        return isinstance(self, Car)
        
    def isTruck(self):
        return isinstance(self, Truck)
        
    def getX(self):
        return self.__x
        
    def setX(self, x):
        try:
            self.__x = int(x)
        except:
            raise InterpreterError('The parameter of setX must be an integer. Usage: setX(x)')
            
    def getY(self):
        return self.__y
        
    def setY(self, y):
        try:
            self.__y = int(y)
        except:
            raise InterpreterError('The parameter of setY must be an integer. Usage: setY(y)')
            
    def getDirection(self):
        return self.__direction
        
    def setDirection(self, direction):
        try:
            self.__direction = int(direction) % 8
        except:
            raise InterpreterError('The parameter of setDirection must be an integer. Usage: setDirection(direction)')
            
    def __getDirectionDelta(self, direction):
        if direction == 0:
            return [ 1, 0]
        elif direction == 1:
            return [ 1, 1]
        elif direction == 2:
            return [ 0, 1]
        elif direction == 3:
            return [-1, 1]
        elif direction == 4:
            return [-1, 0]
        elif direction == 5:
            return [-1,-1]
        elif direction == 6:
            return [ 0,-1]
        elif direction == 7:
            return [ 1,-1]
        else:
            raise InterpreterError('Unknown direction! Internal error ...')
            
    def pick(self, direction):
        picked = Collection()
        [dx, dy] = self.__getDirectionDelta(direction)
        for item in self.__world.all:
            if self.__x == item.getX() + dx and self.__y == item.getY() + dy:
                picked.add(item)
        return picked
        
    def pickForward(self):
        return self.pick(self.__direction)
        
    def pickBackward(self):
        return self.pick((self.__direction + 4) % 8)
        
    def pickNeighbours(self):
        neighbours = Collection()
        for direction in range(0, 8):
            neighbours.addList(self.pick(direction))
        return neighbours
        
    def pickOver(self):
        over = Collection()
        for item in self.__world.all:
            if self.__x == item.getX() and self.__y == item.getY() and item != self:
                over.add(item)
        return over
        
    def forward(self):
        [dx, dy] = self.__getDirectionDelta(self.__direction)
        self.__x += dx
        self.__y += dy
        
    def backward(self):
        [dx, dy] = self.__getDirectionDelta(self.__direction)
        self.__x -= dx
        self.__y -= dy
        
    def turn(self, delta = 1):
        try:
            self.__direction += int(delta)
        except:
            raise InterpreterError('The parameter of turn must be an integer. Usage: turn(delta)')
        self.__direction %= 8
        
# ******************************************************************************
# Class Car
# ******************************************************************************
class Car(WorldObject):
    def __init__(self, world, x = 0, y = 0, direction = 0):
        WorldObject.__init__(self, world, x, y, direction)
        
# ******************************************************************************
# Class Truck
# ******************************************************************************
class Truck(WorldObject):
    def __init__(self, world, x = 0, y = 0, direction = 0):
        WorldObject.__init__(self, world, x, y, direction)
        
# ******************************************************************************
# Class Simulator
# ******************************************************************************
class Simulator:
    def __init__(self, width, height):
        pygame.display.set_caption('Trucky')
        self.__screen = pygame.display.set_mode([int(width * 30), int(height * 30)])
        self.__car = []
        self.__truck = []
        for i in range(0, 8):
            self.__car.append(pygame.image.load('images/car_%s.png' % i))
            self.__truck.append(pygame.image.load('images/truck_%s.png' % i))
            
    def paint(self, world, delay):
        self.__screen.fill((world.getColor().getR(), world.getColor().getG(), world.getColor().getB()))
        [w, h] = self.__screen.get_size()
        for item in world.all:
            if isinstance(item, Car):
                self.__screen.blit(self.__car[item.getDirection()], (item.getX() * 30, h - ((item.getY() + 1) * 30)))
            else:
                self.__screen.blit(self.__truck[item.getDirection()], (item.getX() * 30, h - ((item.getY() + 1) * 30)))
        pygame.display.flip()
        
        start = time()
        while(time() - start < delay):
            for event in pygame.event.get():
                if event.type == QUIT:
                    import sys
                    sys.exit()