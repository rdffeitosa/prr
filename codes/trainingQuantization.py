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
import pickle
import bz2
import multiprocessing
from functools import partial
from collections import OrderedDict
import time

sys.path.append('include')
import executionDetails
import colorQuantization
import vectorQuantization
import messagesColors

def colorVectorQuantizationHelper(filePath, nColors, clustersVectors):
    rawData = io.imread(filePath)
    nDimensions = numpy.ndim(rawData)
    
    if nDimensions == 3:
        rawData = 0.2125 * rawData[:,:,0] + 0.7154 * rawData[:,:,1] + 0.0721 * rawData[:,:,2]
        rawData = rawData.astype(numpy.uint8)
    
    colorQuantizationImage = colorQuantization.colorQuantization(rawData, nColors)
    indexesListQuantization = vectorQuantization.vectorQuantization(colorQuantizationImage, clustersVectors, indexesListMode=True)
    
    return indexesListQuantization

def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-folder <input folder with images for quantization> --quantization-colors <number of colors> --training-file <training data file> [--number-processes <number of parallel processes>]' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-folder=', 'quantization-colors=', 'training-file=']
    optionalOptions = ['number-processes=']
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
        if opt == '--input-folder':
            folderPath = arg
            if folderPath[-1] != '/':
                folderPath += '/'
        elif opt == '--quantization-colors':
            nColors = int(arg)
        elif opt == '--training-file':
            trainingFilename = arg
            
            if os.path.isfile(trainingFilename):
                print 'Opening training data file'
                
                trainingFile = bz2.BZ2File(trainingFilename, 'rb')
                trainingData = pickle.load(trainingFile)
                trainingFile.close()
            else:
                print messagesColors.ERROR + 'Training data file not found' + messagesColors.END
                sys.exit(2)
        elif opt == '--number-processes':
            nProcesses = int(arg)
            if nProcesses > multiprocessing.cpu_count():
                nProcesses = multiprocessing.cpu_count()
    
    detailsFilename = folderPath + '../../../quantizationsDetails'
    executionDetails.environmentDetails(detailsFilename, lineOptions)
    executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
    
    pool = multiprocessing.Pool(nProcesses)
    
    classList = os.listdir(folderPath)
    classList.sort()
        
    fileTypes = ['bmp', 'jpg', 'jpeg', 'png']
    filesList = []
    for className in classList:
        for fileType in fileTypes:
            filesList += glob.glob(folderPath + className + '/*.' + fileType)
    filesList.sort()
        
    filenames = []
    for filePath in filesList:
        filename = os.path.basename(filePath)
        filenames.append(filename)
    
    quantizationsData = OrderedDict()

    vectorsCodebooksSizes = trainingData.keys()
    for vectorCodebookSize in vectorsCodebooksSizes:
        vectorSize = vectorCodebookSize[0]
        codebookSize = vectorCodebookSize[1]
        
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Quantizing images for vector size ' + str(vectorSize) + 'x' + str(vectorSize) + ' and codebook with ' + str(codebookSize) +  ' symbols ###' + messagesColors.END])
        startTime = time.time()
        
        quantizationsData[vectorCodebookSize] = OrderedDict()

        nClasses = len(trainingData[vectorCodebookSize].keys())
        
        k = 0
        sys.stdout.write('\r%s%d%s' % ('Perfoming color and vector quantizations ', int(round(float(k)/nClasses*100)), '%'))
        sys.stdout.flush()
        
        for className, codebookDistortion in trainingData[vectorCodebookSize].items():
            clustersVectors = codebookDistortion['codebook']
            quantizedImages = pool.map(partial(colorVectorQuantizationHelper, nColors=nColors, clustersVectors=clustersVectors), filesList)
            quantizationsData[vectorCodebookSize][className] = OrderedDict(zip(filenames, quantizedImages))
                
            k += 1
            sys.stdout.write('\r%s%d%s' % ('Perfoming color and vector quantizations ', int(round(float(k)/nClasses*100)), '%'))
            sys.stdout.flush()
        
        print ''
        
        elapsedTime = executionDetails.calcTime(startTime, time.time())
        executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Elapsed time: ' + elapsedTime + messagesColors.END])
        
    print 'Saving quantizations data file'
    
    quantizationsFile = bz2.BZ2File(folderPath + '../../../quantizationsData.pckl.bz2', 'wb')
    pickle.dump(quantizationsData, quantizationsFile)
    quantizationsFile.close()
    
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    main(sys.argv[1:])