# Author: Annabel Revers
# Date:   August 2021

import ast
import sys
import os

# initializeMemory(type_info): returns initialized memory and updates the values of type_info keys for use in
    # Parameters:
        # type_info: a dictionary which, for every variable that you see, has its type
    # Returns:
        # a list of zeros of the size needed to store the given variables
def initializeMemory(type_info):
    # initialize memory
    memory = []
    # add space to memory
    i = 0
    for key,value in type_info.items():
        # split by sum type
        sums = value.split('|')
        # find largest type
        largest = 1
        for x in range(len(sums)):
            length = sums[x].count(',') + 1
            if length > largest:
                largest = length
        # add space for tag if sum type
        if len(sums) > 1:  
            largest += 1
        # add space for variable value
        for z in range(largest):
            memory.append(0)
        # update type_info value to a tuple, the first element being a list of types split by '|' and the second element the variable's offset
        type_info[key] = (sums,i)
        i += largest
    return memory

# writeToMemory(type_info,values,memory): writes variable types and values to memory
    # Parameters:
        # type_info: same value as passed to initializeMemory but now updated
        # values: dictionary where the keys are variable names and the values are the variable values
        # memory: the memory intialized with all 0s by intializeMemory
    # Returns:
        # an array with the values and tags (if sum type) of the variables
def writeToMemory(type_info, values, memory):
    for key,value in values.items():
        # get variable's information
        sums = type_info[key][0]
        index = type_info[key][1]
        # check if we need a tag in memory
        if len(sums) > 1:
            tag = value[0]
            for i in range(len(sums)):
                if sums[i] == tag:
                    memory[index] = i
                    mytype = sums[i]
                    break
            index += 1
            myval = value[1]
        else: 
            mytype = sums[0]
            myval = value
        # add values to memory
        if not isinstance(myval, list) == 1: # int or char
            if mytype == 'char':
                memory[index] = ord(myval)
            else: 
                memory[index] = myval
        else: # product
            mytype = mytype.split(',')
            for j in range(len(mytype)):
                if mytype[j] == 'char':
                    memory[index] = ord(myval[j])
                else: 
                    memory[index] = myval[j]
                index += 1 
    return memory

# readFromMemory(type_info,memory): reads variable types and values from memory
    # Paramters:
        # same arguments as writeToMemory
    # Returns:
        # a dictionary of variables and their values and tags (if sum type) equal to what the 'values' paramter was in writeToMemory
def readFromMemory(type_info, memory):
    # intialize dictionary to store variables and values from memory
    readmemory = {}
    # loop through variables and retrieve their information from memory
    for key,value in type_info.items(): 
        sums = value[0]
        index = value[1]
        # get tag from memory if sum type
        if len(sums) > 1: 
            mytype = sums[memory[index]]
            tagged = True
            index += 1
        else : 
            mytype = sums[0]
            tagged = False
        # add variable information to dictionary
        if mytype.count(',') == 0: # plain int or char
            if mytype == 'char':
                myval = chr(memory[index])
            else:
                myval = memory[index]
            if tagged:
                readmemory[key] = (mytype,myval)
            else: 
                readmemory[key] = myval
        else: # product type
            values = []
            separatedtypes = mytype.split(',')
            for t in separatedtypes:
                if t == 'char': # char
                    values.append(chr(memory[index]))
                else: # int
                    values.append(memory[index])
                index += 1
            if tagged:
                readmemory[key] = (mytype,values)
            else:
                readmemory[key] = values
    return readmemory

# checkValidMemory(memory): checks that memory is valid
    # Parameters:
        # memory array after it has been passed to writeToMemory
    # Returns:
        # Nothing, only raises errors
def checkValidMemory(memory):
    # check that memory is list, raise error if not
    ok = isinstance(memory,list)
    if not ok: raise(RuntimeError("Invalid memory, not a list: {}".format(memory)))
    # check that all indices are int within size range, raise error if not
    for i in memory:
        ok = isinstance(i,int)
        if not ok: raise(RuntimeError("Invalid memory, element not an int: {}".format(i)))
        ok = i >= 0 and i < 2**32
        if not ok: raise(RuntimeError("Invalid memory, integer element not a word: {}".format(i)))

# runSingleTestSet(): runs all above functions on test variables
    # Parameters:
        # type_info: dictionary with variables and their types
        # data_list: dictionary with variables and their values
        # constantSize: boolean that determines if memory should stay same size
    # Return:
        # True if test is sucessful, otherwise False
def runSingleTest(type_info, data_list, constantSize):
    mem = initializeMemory(type_info)
    checkValidMemory(mem) 
    size = len(mem)
    allData = {}
    for data in data_list:
        mem = writeToMemory(type_info.copy(), data.copy(), mem.copy())
        checkValidMemory(mem)
        if constantSize and size != len(mem):
            raise(RuntimeError("Size of memory changed after initialisation"))
        allData.update(data)
        memData = readFromMemory(type_info, mem)
        for k,v in allData.items():
            if not (type(memData[k]) == type(v) and memData[k] == v):
                raise(RuntimeError("The value of {} wasn't retrieved properly".format(k)))
    return True

# testSet(): tests above functions with several different sets of variables
# Parameters:
    # None
# Returns:
    # Nothing
def testSet():
    """ This is code to test the functions. """
    # Example 1a: plain int values, write once
    type_info = {'x':'int','y':'int','z':'int'}
    data = {'x':3,'y':200,'z':50}
    runSingleTest(type_info, [data], True)
    # Example 1b: plain int values, incremental updates
    type_info = {'x':'int','y':'int','z':'int'}
    runSingleTest(type_info, [{'x':3,'z':50},{'y':200,'z':50},{'z':20}], True)
    # Example 1c: plain char values, write once
    type_info = {'x':'char','y':'char','z':'char'}
    data = {'x':'3','y':'a','z':'x'}
    runSingleTest(type_info, [data], True)

    # Example 2: product types
    type_info = {'x':'int,int','y':'int','z':'int,int,int'}
    data = {'x':[3,4],'y':200,'z':[50,60,70]}
    runSingleTest(type_info, [data], True) 
    
    # Example 3: sum types (tagged)
    type_info = {'x':'int|char','b':'int','z':'int|char'}
    data = {'x':('int',3),'b':200,'z':('char','d')}
    runSingleTest(type_info, [data], True)

    # Example 4: combining sum and product types
    type_info = {'x':'int|char,int','z':'int|char,int'}
    data = {'x':('int',3),'z':('char,int',['/',60])}
    runSingleTest(type_info, [data], True)

    print("Ran all tests!")

# run all tests
testSet()
