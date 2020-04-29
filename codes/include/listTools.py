#!/usr/bin/python

from operator import mul
from scipy.spatial import distance
from collections import OrderedDict

#Author: drewbuntoo
#Source: https://www.codecademy.com/en/forum_questions/52cc75f0631fe98640001510#answer-52d057d380ff3321d8000d47

def flatten(valuesList):
    try:
        interableObject = iter(valuesList)
    except:
        yield valuesList
    else:
        for i in interableObject:
            for j in flatten(i):
                yield j

###### End Author: drewbuntoo ######
                
def prod(iterable):
    return reduce(mul, iterable, 1)

def reshape(valuesList, shape):
    if prod(shape) == len(valuesList):
        reshapedList = list(valuesList)
        for i, dimensionSize in enumerate(reversed(shape)):
            nElements = len(reshapedList)
            if nElements % dimensionSize == 0:
                k = 0
                while k < nElements:
                    elementsGroup = reshapedList[0:dimensionSize]
                    del reshapedList[0:dimensionSize]
                    reshapedList.append(elementsGroup)
                    k += dimensionSize
            else:
               print 'Number of elements incompatible for reshape in dimension ' + str(len(shape) - i)
               return None

        return reshapedList[0]
    else:
        print 'Number of elements incompatible for reshape'

def sort(vectorsList, inverted=False):
    size = len(set(map(len, vectorsList)))
    
    if size == 1:
        dataType = len(set(flatten([set(map(type, vector)) for vector in vectorsList])))
        
        if dataType == 1:
            if inverted:
                referenceValue = max(flatten(vectorsList))
            else:
                referenceValue = min(flatten(vectorsList))
                
            root = [referenceValue for i in range(len(vectorsList[0]))]
            distances = OrderedDict()
            
            for i, vector in enumerate(vectorsList):
                distances[i] = distance.euclidean(root, vector)
            
            vectorsListOrdered = []
            while len(distances) > 0:
                minIndex = distances.keys()[distances.values().index(min(distances.values()))]
                vectorsListOrdered.append(vectorsList[minIndex])
                del distances[minIndex]
            
            return vectorsListOrdered
        else:
            print "The vectors must have the same type"
            return None
    else:
        print "The vectors must have the same size"
        return None

def popColumn(listofList, index):
    return [r.pop(index) for r in listofList]

def addColumn(listofList, column, index):
    for i, r in enumerate(listofList):
        r.insert(index, column[i])
        
def checkEqualElements(valuesList):
    if len(set(valuesList)) == 1:
        return True
    else:
        return False