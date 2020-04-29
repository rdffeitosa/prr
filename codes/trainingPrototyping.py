#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

from skimage import io
import sys
import getopt
import os
import glob
import numpy
import math
from collections import OrderedDict
import pickle
import multiprocessing
from functools import partial
from itertools import repeat
import bz2
import re
import time

sys.path.append('include')
import executionDetails
import colorQuantization
import lbg
import listTools
import messagesColors


def prepareScenario(scenarioStr):
    scenarioStr = scenarioStr[1:-1]
    scenarioStr = scenarioStr.split('), (')
    for i, classParameter in enumerate(scenarioStr):
        scenarioStr[i] =re.sub('[()\'\s]', '', scenarioStr[i])
        
    scenarioTuple = tuple()
    for classParameter in scenarioStr:
        classParameter = classParameter.split(',')
        scenarioParameter = tuple()
        
        for parameter in classParameter[1:3]:
            scenarioParameter = scenarioParameter + (int(parameter),)
        scenarioTuple = scenarioTuple + ((classParameter[0], scenarioParameter),)
    
    return scenarioTuple

def generateCodebookUnpack(args):
    return lbg.generate_codebook(*args)

def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-folder <folder path with images for training> --quantization-colors <number of colors> --training-convergence <convergence value> [--vectors-sizes <vectors sizes> --codebooks-sizes <number of symbols> --classes-parameters <classes and your specific parameters in a list of tuples "((\'classname\', (vector size, codebook size)), (\'classname\', (vector size, codebook size)), ..., (\'classname\', (vector size, codebook size)))"> --number-processes <number of parallel processes>]' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-folder=', 'quantization-colors=', 'training-convergence=']
    optionalOptions = ['vectors-sizes=', 'codebooks-sizes=', 'classes-parameters=', 'number-processes=']
    try:
        lineOptions, lineArguments = getopt.getopt(argv,'', requiredOptions + optionalOptions)
        opts = [opt for opt, arg in lineOptions]
        for option in requiredOptions:
            option = '--' + option[:-1]
            if option not in opts:
                print messagesColors.ERROR + 'Error: ' + option + ' option is required' + messagesColors.END
                usage()
    except getopt.GetoptError:
        usage()
        
    executionParameters = ''
    nProcesses = 1
    for opt, arg in lineOptions:
        if opt == '--input-folder':
            folderPath = arg
            if folderPath[-1] != '/':
                folderPath += '/'
        elif opt == '--quantization-colors':
            executionParameters += opt[2:] + '=' + arg + ', '
            nColors = int(arg)
        elif opt == '--training-convergence':
            executionParameters += opt[2:] + '=' + arg + ', '
            trainingConvergence = float(arg)
        elif opt == '--vectors-sizes':
            executionParameters += opt[2:] + '=[' + arg + '], '
            vectorsSizes = map(int, arg.split())
        elif opt == '--codebooks-sizes':
            executionParameters += opt[2:] + '=[' + arg + '], '
            codebooksSizes = map(int, arg.split())
        elif opt == '--classes-parameters':
            classesParameters = prepareScenario(arg)
            classesParameters = list(classesParameters)
            classesParameters.sort(key=lambda tup:tup[0])
            classesParameters = tuple(classesParameters)
        elif opt == '--number-processes':
            nProcesses = int(arg)
            if nProcesses > multiprocessing.cpu_count():
                nProcesses = multiprocessing.cpu_count()
    
    
    if 'vectorsSizes' in locals() and 'codebooksSizes' in locals():
        trainingMode = 'full'
    elif 'classesParameters' in locals():
        trainingMode = 'validated'
    else:
        print messagesColors.ERROR + 'Error: Enter sets of vectors and codebooks sizes or a list of tuples with the classes and your specific parameters' + messagesColors.END
        usage()
    
    detailsFilename = folderPath + '../../../trainingDetails.txt'
    executionDetails.environmentDetails(detailsFilename, lineOptions)
    executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
    
    if trainingMode == 'full':
        classList = os.listdir(folderPath)
        classList.sort()
    else:
        classList = []
        for className, parameters in classesParameters:
            classList.append(className)
        classList = list(set(classList))
        classList.sort()
    
    if trainingMode == 'full':
        if nProcesses > len(classList):
            nProcesses = len(classList)
            executionDetails.outputDetails(detailsFilename, [messagesColors.WARNING + 'WARNING: Allocating only ' + str(nProcesses) + ' processes for classes training' + messagesColors.END])
    else:
        if nProcesses > len(classesParameters):
            nProcesses = len(classesParameters)
            executionDetails.outputDetails(detailsFilename, [messagesColors.WARNING + 'WARNING: Allocating only ' + str(nProcesses) + ' processes for classes training' + messagesColors.END])
    
    pool = multiprocessing.Pool(nProcesses)

    fileTypes = ['bmp', 'jpg', 'jpeg', 'png']
    filesList = []
    for className in classList:
        for fileType in fileTypes:
            filesList += glob.glob(folderPath + className + '/*.' + fileType)
    filesList.sort()
    
    executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Color Quantization ###' + messagesColors.END, 'Performing color quantization of training images'])

    imageData = []
    for filePath in filesList:
        rawData = io.imread(filePath)
        nDimensions = numpy.ndim(rawData)
        
        if nDimensions == 3:
            rawData = 0.2125 * rawData[:,:,0] + 0.7154 * rawData[:,:,1] + 0.0721 * rawData[:,:,2]
            rawData = rawData.astype(numpy.uint8)
        
        imageData.append(rawData)
    
    imageData = pool.map(partial(colorQuantization.colorQuantization, nClusters_=nColors), imageData)
    imageData = OrderedDict(zip(filesList, imageData))
    
    if trainingMode == 'full':
        for vectorSize in vectorsSizes:
            startTime = time.time()
            
            trainingData = OrderedDict()
            
            executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Training for vector size ' + str(vectorSize) + 'x' + str(vectorSize) + ' ###' + messagesColors.END, 'Collecting vectors of training images'])
            
            trainingSamples = OrderedDict()
            for className in classList:
                classFiles = filter(lambda k: folderPath + className in k, filesList)
                trainingSamples[className] = []
                
                for filePath in classFiles:
                    rawData = imageData[filePath].astype(float)
                    nRows = rawData.shape[0]
                    nColumns = rawData.shape[1]
                    
                    nWindowX = int(math.ceil(float(nColumns)/vectorSize))
                    nWindowY = int(math.ceil(float(nRows)/vectorSize))
                        
                    for y in range(nWindowY):
                        for x in range(nWindowX):
                            startShapeX = x * vectorSize
                            startShapeY = y * vectorSize
                            endShapeX = startShapeX + vectorSize
                            endShapeY = startShapeY + vectorSize
                            
                            while (endShapeX > nColumns + 1):
                                endShapeX -= 1
                            while (endShapeY > nRows + 1):
                                endShapeY -= 1
                            
                            pixelsBlock = rawData[startShapeY:endShapeY,startShapeX:endShapeX]
                            while pixelsBlock.shape[0] < vectorSize:
                                pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[-1,:], axis=0)
                            while pixelsBlock.shape[1] < vectorSize:
                                pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[:,-1], axis=1)
                            
                            trainingSamples[className].append(pixelsBlock.flatten().tolist())
            
            trainingSamples = list(trainingSamples.values())
            
            executionDetails.outputDetails(detailsFilename, ['Generating codebooks'])
                
            codebooks = pool.map(partial(lbg.generate_codebook, size_codebook=codebooksSizes, epsilon=trainingConvergence), trainingSamples)
            
            for codebookSize in codebooksSizes:
                trainingData[(vectorSize, codebookSize)] = OrderedDict()
                for className in classList:
                    trainingData[(vectorSize, codebookSize)][className] = OrderedDict()
            
            for i, codebook in enumerate(codebooks):
                for codebookSize in codebooksSizes:
                    trainingData[(vectorSize, codebookSize)][classList[i]]['codebook'] = listTools.sort(codebook[codebookSize][0])
                    trainingData[(vectorSize, codebookSize)][classList[i]]['distortion'] = codebook[codebookSize][1]
                    
            trainingFile = bz2.BZ2File(folderPath + '../../../trainingData_' + str(vectorSize) + '_tmp.pckl.bz2', 'wb')
            pickle.dump(trainingData, trainingFile)
            trainingFile.close()
                    
            elapsedTime = executionDetails.calcTime(startTime, time.time())
            executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Elapsed time: ' + elapsedTime + messagesColors.END])
        
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Finishing ###' + messagesColors.END, 'Saving training data file'])
    
        trainingData = OrderedDict()
        for vectorSize in vectorsSizes:
            trainingFileAux = bz2.BZ2File(folderPath + '../../../trainingData_' + str(vectorSize) + '_tmp.pckl.bz2', 'rb')
            trainingDataAux = pickle.load(trainingFileAux)
            trainingFileAux.close()
             
            trainingData.update(trainingDataAux)
         
        trainingFile = bz2.BZ2File(folderPath + '../../../trainingData.pckl.bz2', 'wb')
        pickle.dump(trainingData, trainingFile)
        trainingFile.close()
         
        for vectorSize in vectorsSizes:
            os.remove(folderPath + '../../../trainingData_' + str(vectorSize) + '_tmp.pckl.bz2')
    else:
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Training for ' + str(classesParameters) + ' ###' + messagesColors.END, 'Collecting vectors of training images'])
        
        trainingSamples = OrderedDict()
        trainingData = OrderedDict()
        codebookSizes = []
        
        for className, parameters in classesParameters:
            startTime = time.time()
            
            vectorSize = parameters[0]
            codebookSize = parameters[1]
            codebookSizes.append(codebookSize)
            
            classFiles = filter(lambda k: folderPath + className in k, filesList)
            trainingSamples[(className, parameters)] = []
            
            
            for filePath in classFiles:
                rawData = imageData[filePath].astype(float)
                nRows = rawData.shape[0]
                nColumns = rawData.shape[1]
                
                nWindowX = int(math.ceil(float(nColumns)/vectorSize))
                nWindowY = int(math.ceil(float(nRows)/vectorSize))
                    
                for y in range(nWindowY):
                    for x in range(nWindowX):
                        startShapeX = x * vectorSize
                        startShapeY = y * vectorSize
                        endShapeX = startShapeX + vectorSize
                        endShapeY = startShapeY + vectorSize
                        
                        while (endShapeX > nColumns + 1):
                            endShapeX -= 1
                        while (endShapeY > nRows + 1):
                            endShapeY -= 1
                        
                        pixelsBlock = rawData[startShapeY:endShapeY,startShapeX:endShapeX]
                        while pixelsBlock.shape[0] < vectorSize:
                            pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[-1,:], axis=0)
                        while pixelsBlock.shape[1] < vectorSize:
                            pixelsBlock = numpy.insert(pixelsBlock, -1, values=pixelsBlock[:,-1], axis=1)
                        
                        trainingSamples[(className, parameters)].append(pixelsBlock.flatten().tolist())
            
        trainingSamples = list(trainingSamples.values())
            
        executionDetails.outputDetails(detailsFilename, ['Generating codebooks'])
                
        codebooks = pool.map(generateCodebookUnpack, zip(trainingSamples, codebookSizes, repeat(trainingConvergence)))
        
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Finishing ###' + messagesColors.END, 'Saving training data file'])
                
        elapsedTime = executionDetails.calcTime(startTime, time.time())
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Elapsed time: ' + elapsedTime + messagesColors.END])
            
        for i, codebook in enumerate(codebooks):
            className = classesParameters[i][0]
            parameters = classesParameters[i][1]

            if parameters not in trainingData.keys():
                trainingData[parameters] = OrderedDict()
                trainingData[parameters][className] = OrderedDict()               
                trainingData[parameters][className]['codebook'] = listTools.sort(codebook.values()[0][0])
                trainingData[parameters][className]['distortion'] = codebook.values()[0][1]
            else:
                trainingData[parameters][className] = OrderedDict()
                trainingData[parameters][className]['codebook'] = listTools.sort(codebook.values()[0][0])
                trainingData[parameters][className]['distortion'] = codebook.values()[0][1]
        
        trainingFile = bz2.BZ2File(folderPath + '../../../trainingData.pckl.bz2', 'wb')
        pickle.dump(trainingData, trainingFile)
        trainingFile.close()
    
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    
    main(sys.argv[1:])