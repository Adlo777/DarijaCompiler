#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Parser as vslparse


'''
  Darija Compiler Project 
  ECOLE NATIONALE DES SCIENCES APPLIQUEES
  WIAM-IBTISSAM-ADMEO
'''


# Optimize a byte code (supress double-label)
def optimizeLabel():
    '''optimize the byte code given with delete double label'''
    import re
    global lines
    label = r'([A-Za-z0-9_]+)'
    re_dlabel = re.compile(r'^'+label+': '+label+': ')
    double=True
    # While we found restart the search
    while(double):
        double = False
        for nb,line in enumerate(lines):
            match = re_dlabel.match(line)
            # If we found two label
            if match:
                doubles = match.groups()
                lines[nb] = line.replace(line[:len(doubles[0])+2],'')   # Delete the first label
                for nb,l in enumerate(lines):
                    lines[nb] = l.replace(doubles[0],doubles[1])    # Search all the jump in the first label
                double=True
                break

# Optimize 'label: JMP ....'
def optimizeLabelJmp():
    global lines
    import re
    re_opset = re.compile(r'[A-Za-z0-9_]+: JMP [A-Za-z0-9_]+')
    found = True
    # While found one sequence, 
    while(found):
        found = False
        for nb, line in enumerate(lines):
            match = re_opset.findall(line)
            # If we found the sequence 'label: JMP label:'
            if len(match)==1:
                lastlabel = match[0].split(' ')[0][:len(match[0].split(' ')[0])-1]
                if lastlabel not in [f.name for f in vslparse.functiondef]:
                    found = True
                    newlabel = match[0].split(' ')[2]
                    lines[nb] = lines[nb].replace(lastlabel+': ','')
                    re_jump = re.compile(r'J(?:MP|N?Z) '+lastlabel)
                    # Search for replace the new label jump
                    for n,l in enumerate(lines):
                        find = re_jump.findall(l)
                        if len(find)==1:
                            s=find[0].split(' ')
                            lines[n]= s[0]+' '+newlabel

# Optimize the set-get
def optimizeSetGet():
    '''Optimize set and get'''
    import re
    global lines
    re_opset = re.compile(r'SET[LGP] [0-9]+')
    finals = []
    skipNext=False
    for nb, line in enumerate(lines):
        match = re_opset.findall(line)
        # If found a set with the same get before
        if len(match)==1 and lines[nb+1]=='GET'+match[0][3:]:
            finals.append(line.replace(match[0],'SETN'+match[0][3:])) # Set the identifier but do not pop the stack
            skipNext = True
        else:
            if not skipNext: finals.append(line)
            else: skipNext=False    # Skip this opcode
    lines = finals

# Optimize 'GET - SET'
def optimizeGetSet():
    '''Optimize get and set'''
    import re
    global lines
    re_opset = re.compile(r'GET[LGP] [0-9]+')
    finals = []
    skipNext=False
    for nb, line in enumerate(lines):
        match = re_opset.findall(line)
        # If found a set with the same get before
        if not len(match)==1 or lines[nb+1]!='SET'+match[0][3:]:
            if not skipNext: finals.append(line)
            else: skipNext=False
        else:
            skipNext=True    # Skip this opcode (SET)
    lines = finals

# Optimize a byte code given
def optimize(byte,level=3):
    '''optimize the byte code given with the given level'''
    global lines
    # Load the lines
    lines = byte.splitlines()
    # Need by the virtual machine
    optimizeLabel()
    # Optimize with level
    if level>0: optimizeLabelJmp()
    if level>1: optimizeSetGet()
    if level>2: optimizeGetSet()
    return '\n'.join(lines)
