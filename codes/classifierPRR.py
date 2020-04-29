#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import time
import sys
import getopt
import pickle
import bz2
import re
import os
import multiprocessing
import glob
from collections import OrderedDict
from shutil import rmtree, copy2
from skimage import io
import numpy
import math
import string
import random
import warnings
from tabulate import tabulate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

sys.path.append('include')
import messagesColors
import executionDetails
from colorQuantization import colorQuantization
from vectorQuantization import vectorQuantization, imageQuantization
import integerLZW
import HuffmanCoding
from listTools import flatten


def scenarioClasses(scenario):
    classNames = '['
    for className, parameters in scenario:
        classNames += className + ', '
    classNames = classNames[:-2]
    classNames += ']'
    
    return classNames

def prepareScenario(scenarioStr):
    scenarioStr = scenarioStr[1:-1]
    scenarioStr = scenarioStr.split('), (')
    for i, classParameter in enumerate(scenarioStr):
        scenarioStr[i] =re.sub('[()\'\s]', '', scenarioStr[i])
        
    scenarioTuple = tuple()
    for classParameter in scenarioStr:
        classParameter = classParameter.split(',')
        scenarioParameter = tuple()
        
        for parameter in classParameter[1:]:
            scenarioParameter = scenarioParameter + (int(parameter),)
        scenarioTuple = scenarioTuple + ((classParameter[0], scenarioParameter),)
    
    return scenarioTuple

def LZWHuffman(indexesList, compressionDictionary):
    indexesList = list(flatten(indexesList))
    
    compressedData_ = integerLZW.dataCompressing(compressionDictionary, indexesList)
    compressedData_, huffmanDict = HuffmanCoding.dataCompressing(compressedData_)

    dictionaryLength = len(compressionDictionary.keys())
    nBits = int(math.floor(math.log(dictionaryLength - 1) / math.log(2) ) + 1)
    
    bitsRawData = len(indexesList) * nBits
    bitsCompressedData = len(compressedData_)
    
    compressionRatio = float(bitsRawData) / bitsCompressedData * -1
    
    return compressionRatio

def embedCompressor(indexesList, clustersVectors, folderPath, compressionEngines):
    quantizedImage = imageQuantization(indexesList, clustersVectors)
    
    filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))
    filePath = folderPath + 'tmp/' + filename + '.bmp'
    savePath = folderPath + 'tmp/' + filename + '.compress'
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        io.imsave(filePath, quantizedImage)
    
    if 'zip' in compressionEngines:
        os.system('zip -q ' + savePath + ' ' + filePath)
        compressionSize = os.path.getsize(savePath)
    if 'gzip' in compressionEngines:
        os.system('gzip -ck ' + filePath + ' > ' + savePath)
        compressionSize = os.path.getsize(savePath)
    if 'bzip2' in compressionEngines:
        os.system('bzip2 -czk ' + filePath + ' > ' + savePath)
        compressionSize = os.path.getsize(savePath)
    
    os.remove(filePath)
    os.remove(savePath)
    
    return compressionSize

def compressionHelper(indexesList, clustersVectors, compressionDictionary, folderPath, compressionEngine):    
    if compressionEngine in ['zip', 'gzip', 'bzip2']:
        compressionValue = embedCompressor(indexesList, clustersVectors, folderPath, compressionEngine)
    elif compressionEngine == 'LZWHuffman':
        compressionValue = LZWHuffman(indexesList, compressionDictionary)
    
    return compressionValue

def frequencyDictionary(indexesList):
    indexHistogram = {}
    
    for index in indexesList:
        if index not in indexHistogram:
            indexHistogram[index] = 0
        indexHistogram[index] += 1
    
    return indexHistogram

def entropyHelper(indexesList):
    indexesList = list(flatten(indexesList))
    indexHistogram = frequencyDictionary(indexesList)
    nIndexes = sum(indexHistogram.values())    
    
    H = 0
    for indexFrequency in indexHistogram.values():
        Pr = float(indexFrequency)/nIndexes
        H += Pr * math.log(Pr, 2)

    if H > 0:    
        H *= -1
    
    return H

def colorVectorQuantization(filePath, nColors, clustersVectors):
    rawData = io.imread(filePath)
    nDimensions = numpy.ndim(rawData)
    
    if nDimensions == 3:
        rawData = 0.2125 * rawData[:,:,0] + 0.7154 * rawData[:,:,1] + 0.0721 * rawData[:,:,2]
        rawData = rawData.astype(numpy.uint8)
    
    colorQuantizationImage = colorQuantization(rawData, nColors)
    
    indexesListQuantization = vectorQuantization(colorQuantizationImage, clustersVectors, indexesListMode=True)
    
    return indexesListQuantization

def classificationHelper(filePath, nColors, trainingData, folderPath, measureEngine, classesParametersStr):
    classNames = trainingData.keys()
    
    valueReference = None
    for className in classNames:
        clustersVectors = trainingData[className]
        indexesList = colorVectorQuantization(filePath, nColors, clustersVectors)
        
        if measureEngine in ['zip', 'gzip', 'bzip2', 'LZWHuffman']:
            codebookSize = len(clustersVectors)
            compressionDictionary = OrderedDict({i: i for i in range(codebookSize)})
            
            fileValue = compressionHelper(indexesList, clustersVectors, compressionDictionary, folderPath, measureEngine)
        elif measureEngine in ['entropy']:
            fileValue = entropyHelper(indexesList)
        
        if valueReference == None:
            valueReference = fileValue
            predictedClass = className
        elif fileValue > valueReference:
            valueReference = fileValue
            predictedClass = className
    
    filename = '/' + os.path.basename(filePath)
    
    copy2(filePath, folderPath + predictedClass + filename)
    
def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-folder <folder path with images for classification> --measure-engine <zip, gzip, bzip2, LZWHuffman or entropy> --classes-parameters <tuple of classes and parameters used for classification between "..."> --training-file <training data file> --quantization-colors <number of colors> [--number-processes <number of parallel processes> --id-experiment <identification of experiments> archive-results verbose-mode report-mode]' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-folder=', 'measure-engine=', 'classes-parameters=', 'training-file=', 'quantization-colors=']
    optionalOptions = ['number-processes=', 'id-experiment=', 'archive-results=', 'verbose-mode=', 'report-mode=']
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
        
    archiveResults = False
    verboseMode = False
    reportMode = False
    for arg in lineArguments:
        if arg == 'archive-results':
            archiveResults = True
        if arg == 'verbose-mode':
            verboseMode = True
        if arg == 'report-mode':
            reportMode = True
    
    nProcesses = 1
    for opt, arg in lineOptions:
        if opt == '--input-folder':
            folderPath = arg
            if folderPath[-1] != '/':
                folderPath += '/'
        elif opt == '--measure-engine':
            acceptedMeasureEngines = ['zip', 'gzip', 'bzip2', 'LZWHuffman', 'entropy']
            measureEngine = arg
            
            if measureEngine not in acceptedMeasureEngines:
                if verboseMode:
                    print messagesColors.ERROR + 'Enter a measure engine among the possible ones: ' + str(acceptedMeasureEngines) + messagesColors.END
                sys.exit(2)
        elif opt == '--classes-parameters':
            classesParametersStr = arg
            classesParameters = prepareScenario(classesParametersStr)
        elif opt == '--training-file':
            trainingFilename = arg
            
            if os.path.isfile(trainingFilename):
                if verboseMode:
                    print 'Opening training data file'
                
                trainingFile = bz2.BZ2File(trainingFilename, 'rb')
                trainingData = pickle.load(trainingFile)
                trainingFile.close()
                
                if verboseMode:
                    print 'Selecting classes and parameters'
                
                optimizedTrainingData = OrderedDict()
                try:
                    classNames, parameters = zip(*classesParameters)
                except:
                    if verboseMode:
                        print 'Error on the classes and parameters format'
                    sys.exit(2)
                    
                for k, className in enumerate(classNames):
                    try:
                        optimizedTrainingData[className] = trainingData[parameters[k]][className]['codebook']
                    except:
                        if verboseMode:
                            print 'Classname ' + className + ' or parameters ' + parameters[k] + ' not found in the training file'
                        sys.exit(2)
                
                trainingData = OrderedDict(optimizedTrainingData)
                del optimizedTrainingData
            else:
                if verboseMode:
                    print messagesColors.ERROR + 'Training data file not found' + messagesColors.END
                sys.exit(2)
        elif opt == '--quantization-colors':
            nColors = int(arg)
            if nColors < 2 or nColors > 256:
                print messagesColors.ERROR + 'Enter a value between 2 and 256 for number of quantized colors' + messagesColors.END
                sys.exit(2)
        elif opt == '--number-processes':
            nProcesses = int(arg)
            if nProcesses > multiprocessing.cpu_count():
                nProcesses = multiprocessing.cpu_count()
        
        if opt == '--id-experiment':
            identificationExperiment = arg
        else:
            identificationExperiment = 'None'
    
    if reportMode:
        detailsFilename = folderPath + '../../../classificationReport-id=' + identificationExperiment + ')'
        executionDetails.environmentDetails(detailsFilename, lineOptions)
        executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
    
    dirList = os.listdir(folderPath)
    for value in dirList:
        if os.path.isdir(folderPath + value):
            rmtree(folderPath + value)            
    
    if measureEngine in ['zip', 'gzip', 'bzip2']:
        if os.path.isdir(folderPath + 'tmp'):
            rmtree(folderPath + 'tmp')
        os.mkdir(folderPath + 'tmp')
    
    fileTypes = ['bmp', 'jpg', 'jpeg', 'png']    
    filesList = []
    for fileType in fileTypes:
        filesList += glob.glob(folderPath + '*.' + fileType)
    filesList.sort()
    
    classNames = trainingData.keys()
    selectedFiles = []
    for filePath in filesList:
        filename = os.path.basename(filePath)
        fileClass = filename.split('_')[0]
        if fileClass in classNames:
            selectedFiles.append(filePath)
    nFiles = len(selectedFiles)

    for className in classNames:
        os.mkdir(folderPath + className)
        
    confusionDict = OrderedDict()
    for actualClassName in classNames:
        confusionDict[actualClassName] = OrderedDict()
        for predictedClassName in classNames:
            confusionDict[actualClassName][predictedClassName] = 0
    
    k = 0
    jobs = []
    for filePath in selectedFiles:
        while len(jobs) == nProcesses:
            for job in jobs:
                job.join(timeout=0)
                if not job.is_alive():
                    jobs.remove(job)
                    k += 1
            
            if verboseMode:
                sys.stdout.write('\r%s%d%s' % ('Classifing images ', int(round(float(k)/nFiles*100)), '%'))
                sys.stdout.flush()
        else:
            process = multiprocessing.Process(target=classificationHelper, args=(filePath, nColors, trainingData, folderPath, measureEngine, classesParametersStr,))
            jobs.append(process)
            process.start()
        
    while len(jobs) > 0:
        for job in jobs:
            job.join(timeout=0)
            if not job.is_alive():
                jobs.remove(job)            
                k += 1
                
        if verboseMode:
            sys.stdout.write('\r%s%d%s' % ('Classifing images ', int(round(float(k)/nFiles*100)), '%'))
            sys.stdout.flush()
    
    if os.path.isdir(folderPath + 'tmp'):
        rmtree(folderPath + 'tmp')
    
    yTrue = []
    yPredicted = []
    for predictedClassName in classNames:
        filesList = []
        for fileType in fileTypes:
            filesList += glob.glob(folderPath + predictedClassName + '/*.' + fileType)
            
        for filePath in filesList:
            filename = os.path.basename(filePath)
            actualClassName = filename.split('_')[0]
            
            yTrue.append(classNames.index(actualClassName))
            yPredicted.append(classNames.index(predictedClassName))
                
            confusionDict[actualClassName][predictedClassName] += 1
    
    confusionList = []
    for actualClassName in classNames:
        confusionRow = [actualClassName]
        for predictedClassName in classNames:
            confusionRow.append(confusionDict[actualClassName][predictedClassName])
        confusionList.append(confusionRow)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        accuracy = accuracy_score(yTrue, yPredicted)
        precision = precision_score(yTrue, yPredicted, average='macro')
        recall = recall_score(yTrue, yPredicted, average='macro')
        f1 = f1_score(yTrue, yPredicted, average='macro')

    if not archiveResults:
        dirList = os.listdir(folderPath)
        for value in dirList:
            if os.path.isdir(folderPath + value):
                rmtree(folderPath + value)
    
    if verboseMode:
        print ''
    
    if reportMode:
        executionDetails.outputDetails(detailsFilename, [tabulate(confusionList, headers=classNames, tablefmt='orgtbl')])
    
    if verboseMode:
        print ''

    if reportMode:
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Accuracy: ' + str(accuracy) + messagesColors.END])
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Precision: ' + str(precision) + messagesColors.END])
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Recall: ' + str(recall) + messagesColors.END])
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'F1 Score: ' + str(f1) + messagesColors.END])
    else:
        print 'Accuracy: ' + str(accuracy)
        print 'Precision: ' + str(precision)
        print 'Recall: ' + str(recall)
        print 'F1 Score: ' + str(f1)
       
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    if reportMode:
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    if 'verbose-mode' in sys.argv[1:]:
        print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    main(sys.argv[1:])