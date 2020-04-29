#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import math
import numpy
from scipy.spatial import distance
import listTools

def imageQuantization(indexesList, clustersVectors):
    dataShape = numpy.asarray(indexesList).shape
    nWindowY = dataShape[0]
    nWindowX = dataShape[1]
    
    windowSize = int(math.sqrt(len(clustersVectors[0])))
    nRows = dataShape[0] * windowSize
    nColumns = dataShape[1] * windowSize
    
    quantizedImage = numpy.zeros((nRows, nColumns)).astype(float)
    
    for y in range(nWindowY):
        for x in range(nWindowX):            
            startShapeX = x * windowSize
            startShapeY = y * windowSize
            endShapeX = startShapeX + windowSize
            endShapeY = startShapeY + windowSize
            
            while (endShapeX > nColumns + 1):
                endShapeX -= 1
            while (endShapeY > nRows + 1):
                endShapeY -= 1
        
            windowShape = quantizedImage[startShapeY:endShapeY,startShapeX:endShapeX].shape
            quantizedImage[startShapeY:endShapeY,startShapeX:endShapeX] = numpy.asarray(clustersVectors[indexesList[y][x]]).reshape(windowSize, windowSize)[:windowShape[0], :windowShape[1]]
    vectorizedRound = numpy.vectorize(round)
    quantizedImage = vectorizedRound(quantizedImage).astype(numpy.uint8)
    
    return quantizedImage

def vectorQuantization(rawData_, clustersVectors, indexesListMode=False):
    rawData_ = rawData_.astype(float)
    nRows = rawData_.shape[0]
    nColumns = rawData_.shape[1]
    
    windowSize = int(math.sqrt(len(clustersVectors[0])))
        
    nWindowX = int(math.ceil(float(nColumns)/windowSize))
    nWindowY = int(math.ceil(float(nRows)/windowSize))
    
    dataShape = (nWindowY, nWindowX)
      
    pixelsList = []

    for y in range(nWindowY):
        for x in range(nWindowX):            
            startShapeX = x * windowSize
            startShapeY = y * windowSize
            endShapeX = startShapeX + windowSize
            endShapeY = startShapeY + windowSize
            
            while (endShapeX > nColumns + 1):
                endShapeX -= 1
            while (endShapeY > nRows + 1):
                endShapeY -= 1
            
            pixelsBlock = rawData_[startShapeY:endShapeY, startShapeX:endShapeX]
            while pixelsBlock.shape[0] < windowSize:
                pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[-1,:], axis=0)
            while pixelsBlock.shape[1] < windowSize:
                pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[:,-1], axis=1)
                
            pixelsList.append(pixelsBlock.flatten().tolist())
    
    distancesMatrix = distance.cdist(pixelsList, clustersVectors, metric='euclidean')
    
    indexesList = listTools.reshape(distancesMatrix.argmin(axis=1).tolist(), dataShape)
    
    if indexesListMode:      
        return indexesList
    else:
        quantizedImage = imageQuantization(indexesList, clustersVectors)
        
        return quantizedImage