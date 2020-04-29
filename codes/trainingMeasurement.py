#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import sys
import getopt
import string
import random
import warnings
from skimage import io
from shutil import rmtree
import pickle
import bz2
import os
import multiprocessing
from functools import partial
from collections import OrderedDict
import time
import math

sys.path.append('include')
import executionDetails
import vectorQuantization
from listTools import flatten
import integerLZW
import HuffmanCoding
import messagesColors
from dictTools import getKeys

def embedCompressor(indexesList, clustersVectors, folderPath, measureEngines):
    quantizedImage = vectorQuantization.imageQuantization(indexesList, clustersVectors)
    
    filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))
    filePath = folderPath + 'tmp/' + filename + '.bmp'
    savePath = folderPath + 'tmp/' + filename + '.compress'
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        io.imsave(filePath, quantizedImage)
    
    compressionSizes = OrderedDict()
    if 'zip' in measureEngines:
        os.system('zip -q ' + savePath + ' ' + filePath)
        compressionSizes['zip'] = os.path.getsize(savePath)
    if 'gzip' in measureEngines:
        os.system('gzip -ck ' + filePath + ' > ' + savePath)
        compressionSizes['gzip'] = os.path.getsize(savePath)
    if 'bzip2' in measureEngines:
        os.system('bzip2 -czk ' + filePath + ' > ' + savePath)
        compressionSizes['bzip2'] = os.path.getsize(savePath)
    
    os.remove(filePath)
    os.remove(savePath)
    
    return compressionSizes

def LZWHuffman(indexesList, compressionDictionary):
    indexesList = list(flatten(indexesList))
    
    compressedData = integerLZW.dataCompressing(compressionDictionary, indexesList)
    compressedData, huffmanDict = HuffmanCoding.dataCompressing(compressedData)

    dictionaryLength = len(compressionDictionary.keys())
    nBits = int(math.floor(math.log(dictionaryLength - 1) / math.log(2) ) + 1)
    
    bitsRawData = len(indexesList) * nBits
    bitsCompressedData = len(compressedData)
    
    compressionRatio = (float(bitsRawData) / bitsCompressedData)
    
    return compressionRatio

def frequencyDictionary(indexesList):
    indexHistogram = {}
    
    for index in indexesList:
        if index not in indexHistogram:
            indexHistogram[index] = 0
        indexHistogram[index] += 1
    
    return indexHistogram

def entropy(indexesList):
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

def measuresHelper(indexesList, clustersVectors, compressionDictionary, folderPath, measureEngines):    
    measureValues = OrderedDict()
    
    if not set(measureEngines).isdisjoint(['zip', 'gzip', 'bzip2']):
        measureValues.update(embedCompressor(indexesList, clustersVectors, folderPath, measureEngines))

    if 'LZWHuffman' in measureEngines:
        measureValues['LZWHuffman'] = LZWHuffman(indexesList, compressionDictionary)
    
    if 'entropy' in measureEngines:
        measureValues['entropy'] = entropy(indexesList)
    
    return measureValues
    
def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-data <input with quantizations data file> [--training-file <training data file>] --measure-engines <\'zip gzip bzip2 LZWHuffman entropy\'> [--number-processes <number of parallel processes>]' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-data=', 'measure-engines=']
    optionalOptions = ['training-file=','number-processes=']
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
    
    nProcesses = 1
    for opt, arg in lineOptions:
        if opt == '--input-data':
            quantizationsFilename = arg
            
            if os.path.isfile(quantizationsFilename):               
                folderPath = os.path.dirname(quantizationsFilename) + '/'
                
                print 'Opening quantizations data file'
                
                quantizationsFile = bz2.BZ2File(quantizationsFilename, 'rb')
                quantizationsData = pickle.load(quantizationsFile)
                quantizationsFile.close()
            else:
                print messagesColors.ERROR + 'Quantizations data file not found' + messagesColors.END
                sys.exit(2)
        elif opt == '--training-file':
            trainingFilename = arg
            if os.path.isfile(trainingFilename):
                print 'Opening training data file'
                
                trainingFile = bz2.BZ2File(trainingFilename, 'rb')
                trainingData = pickle.load(trainingFile)
                trainingFile.close()
                
                if os.path.isdir(folderPath + 'tmp'):
                    rmtree(folderPath + 'tmp')
                os.mkdir(folderPath + 'tmp')
            else:
                print 'Training data file not found'
                sys.exit(2)
        elif opt == '--measure-engines':
            acceptedMeasureEngines = ['zip', 'gzip', 'bzip2', 'LZWHuffman', 'entropy']
            measureEngines = arg.split()
            
            for measureEngine in measureEngines:
                if measureEngine not in acceptedMeasureEngines:
                    print messagesColors.ERROR + 'Enter a measure engine among the possible ones: ' + str(acceptedMeasureEngines) + messagesColors.END
                    sys.exit(2)
                
        elif opt == '--number-processes':
            nProcesses = int(arg)
            if nProcesses > multiprocessing.cpu_count():
                nProcesses = multiprocessing.cpu_count()
    
    detailsFilename = folderPath + 'measurementsDetails.txt'
    executionDetails.environmentDetails(detailsFilename, lineOptions)
    executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
      
    pool = multiprocessing.Pool(nProcesses)
    
    classNames = getKeys(quantizationsData, 1)
    nClasses = len(classNames)
    filenames = getKeys(quantizationsData, 2)
    
    measurementsData = OrderedDict()
    
    vectorsCodebooksSizes = quantizationsData.keys() 
    for vectorCodebookSize in vectorsCodebooksSizes:
        vectorSize = vectorCodebookSize[0]
        codebookSize = vectorCodebookSize[1]
        
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Measuring data for vector size ' + str(vectorSize) + 'x' + str(vectorSize) + ' and codebook with ' + str(codebookSize) +  ' symbols ###' + messagesColors.END])
        startTime = time.time()
        
        measurementsData[vectorCodebookSize] = OrderedDict()
        for measureEngine in measureEngines:
            measurementsData[vectorCodebookSize][measureEngine] = OrderedDict()
            for className in classNames:
                measurementsData[vectorCodebookSize][measureEngine][className] = OrderedDict()
            
        compressionDictionary = OrderedDict({i: i for i in range(codebookSize)})

        k = 0
        sys.stdout.write('\r%s%d%s' % ('Measuring data ', int(round(float(k)/nClasses*100)), '%'))
        sys.stdout.flush()
        
        for className in classNames:
            indexesList = quantizationsData[vectorCodebookSize][className].values()
            clustersVectors = trainingData[vectorCodebookSize][className]['codebook']

            measuresValues = pool.map(partial(measuresHelper, clustersVectors=clustersVectors, compressionDictionary=compressionDictionary, folderPath=folderPath, measureEngines=measureEngines), indexesList)

            for i, filename in enumerate(filenames):
                for measureEngine in measureEngines:
                    if measureEngine in ['LZWHuffman']:
                        measureValue = measuresValues[i][measureEngine] * -1
                    else:
                        measureValue = measuresValues[i][measureEngine]
                    measurementsData[vectorCodebookSize][measureEngine][className][filename] = measureValue
            
            k += 1
            sys.stdout.write('\r%s%d%s' % ('Measuring data ', int(round(float(k)/nClasses*100)), '%'))
            sys.stdout.flush()
        
        print ''
        
        elapsedTime = executionDetails.calcTime(startTime, time.time())
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Elapsed time: ' + elapsedTime + messagesColors.END])
    
    print 'Saving measurements data file'
    
    measurementsFile = bz2.BZ2File(folderPath + 'measurementsData.pckl.bz2', 'wb')
    pickle.dump(measurementsData, measurementsFile)
    measurementsFile.close()
    
    if os.path.isdir(folderPath + 'tmp'):
        rmtree(folderPath + 'tmp')
    
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    main(sys.argv[1:])