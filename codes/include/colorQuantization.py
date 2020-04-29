#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import numpy
import math

def clearRepetitions(dataList):
    dataListUnique = []
    for actualValue in dataList:
        if actualValue not in dataListUnique:
            dataListUnique.append(actualValue)
    
    return dataListUnique

def eucledianDistance(pointA, pointB):
    if type(pointA) is not list:
        pointA = [pointA]
        pointB = [pointB]
    
    if len(pointA) != len(pointB):
        print "The points don't have the same dimensionality"
        return False
        
    pointASize = len(pointA)
    sumElement = 0
    for i in range(pointASize):
        sumElement += (pointA[i] - pointB[i]) ** 2
    
    pointDistance = math.sqrt(sumElement)
    
    return pointDistance
    
def sortColors(colorsList):
    sortOrder = None
    
    colorsListSize = len(colorsList)
    if (colorsListSize > 1):
        maxChannelRange = None
        
        try:        
            nColumns = len(colorsList[0])
        except:
            nColumns = 1
        if (nColumns > 1):
        
            for i in range(nColumns):
                rangeLength = max([colorsListRow[i] for colorsListRow in colorsList]) - min([colorsListRow[i] for colorsListRow in colorsList]) #calcula a amplitude de cada canal de cor
                
                if rangeLength > maxChannelRange:
                    maxChannelRange = rangeLength
                    sortOrder = i
        
            colorsList = sorted(colorsList, key=lambda colorChannel: colorChannel[sortOrder])
        else:
            colorsList = sorted(colorsList)
                        
    return colorsList, sortOrder
    
def arrayToList(arrayValues):
    if (type(arrayValues) is numpy.ndarray):
        if (len(arrayValues) > 1):
            nDimensions = numpy.ndim(arrayValues)
            
            if (nDimensions == 2):
                listValues = arrayValues.reshape(-1).tolist()
            elif (nDimensions > 2):
                listValues = arrayValues.reshape(-1, nDimensions).tolist()
            else:
                listValues = arrayValues.tolist()
        
        return listValues
    else:
        print "Input data must be a Numpy Array"
        return None

    
def medianCut(rawData, nClusters):
    if not(math.log(float(nClusters), 10) / math.log(2, 10)).is_integer():
        print "The number of clusters must be power of 2", str(nClusters)
        return False
    
    dataList = arrayToList(rawData)
        
    if (nClusters > len(dataList)):
        print "The number of clusters must be less or equal than the total number of elements"
        return False

    dataClusters = []
    dataClustersAux = []
    dataClusters.insert(0, dataList)
    dataClustersAux.insert(0, dataList)

    contClusters = 1
    while contClusters < nClusters:
        paddingInsertion = 0
        for i in range(contClusters):
            clusterSize = len(dataClusters[i])
            dataClusters[i], sortOrder = sortColors(dataClusters[i])
        
            if clusterSize % 2 == 0:
                medianPoint = int(clusterSize / 2) - 1
            else:
                medianPoint = int(round((clusterSize + 1)/2)) - 1
                
            if (sortOrder):
                criterionOrder = [dataClustersRow[sortOrder] for dataClustersRow in dataClusters[i]]
            else:
                criterionOrder = dataClusters[i]
            
            if (len(criterionOrder) > 1):
                contRepetitionsLeft = 0
                j = medianPoint
                while criterionOrder[j] == criterionOrder[j-1] and j > 0:
                    contRepetitionsLeft += 1
                    j -= 1
            
                contRepetitionsRight = 0
                j = medianPoint
                while criterionOrder[j] == criterionOrder[j+1] and j < clusterSize - 2:
                    contRepetitionsRight += 1
                    j += 1

            if contRepetitionsLeft >= contRepetitionsRight:
                medianPoint += contRepetitionsRight
                cutOff = medianPoint + 1
            else:
                cutOff = medianPoint - contRepetitionsLeft
            
            insertionPoint = i*2+1

            dataClustersAux[i+paddingInsertion] = dataClusters[i][:cutOff]
            dataClustersAux.insert(insertionPoint, dataClusters[i][cutOff:])
            
            paddingInsertion += 1
        
        dataClusters = dataClustersAux[:]

        contClusters *= 2
    
    return dataClusters
    
def findCentroids(rawColors_, nClusters_):
    colorClusters = medianCut(rawColors_, nClusters_)
    
    clustersCentroid = []
    for cluster in colorClusters:
        clusterArray = numpy.array(cluster)
        if len(clusterArray) > 0:
            clustersCentroid.append(clusterArray.mean(0).tolist())
    
    clustersCentroid = clearRepetitions(clustersCentroid)
    nCentroids = len(clustersCentroid)
    
    return clustersCentroid, nCentroids
    
def colorQuantization(rawColors_, nClusters_):    
    nRows = rawColors_.shape[0]
    nColumns = rawColors_.shape[1]
  
    clustersCentroid, nCentroids = findCentroids(rawColors_, nClusters_)
    quantizationDictionary = dict()
    quantizedImage_ = numpy.zeros(rawColors_.shape)

    colorsList = clearRepetitions(arrayToList(rawColors_))
    for color in colorsList:
        pointDistances = []
        for k in range(nCentroids):
            pointDistances.append(eucledianDistance(color, clustersCentroid[k]))
                  
        assignedCluster = pointDistances.index(min(pointDistances))
        quantizationDictionary[str(color)] = clustersCentroid[assignedCluster]
        
    for i in range(nRows):
        for j in range(nColumns):
            quantizedImage_[i][j] = quantizationDictionary[str(rawColors_[i][j].tolist())]
    
    quantizedImage_ = numpy.rint(quantizedImage_).astype(numpy.uint8, copy=False)
    
    return quantizedImage_