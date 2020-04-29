#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import getopt
import sys
import time
import bz2
import pickle
from collections import OrderedDict
import multiprocessing
from functools import partial
import os
import gc

sys.path.append('include')
import messagesColors
import executionDetails
from dictTools import getKeys
import mem_info

def hitRate(scenario, filesList, measureEngine):
    classesParametersHits = {}
    for classParameters in scenario:
        classesParametersHits[classParameters] = 0
    
    evaluatedClasses = filterClasses(scenario)
        
    selectedFiles = []
    for filename in filesList:
        fileClass = filename.split('_')[0]
        if fileClass in evaluatedClasses:
            selectedFiles.append(filename)
    
    for filename in selectedFiles:
        valueReference = None
        for className, parameters in scenario:
            fileValue = measuresData[parameters][measureEngine][className][filename]
            
            if valueReference == None or fileValue > valueReference:
                valueReference = fileValue
                predictedClassParameters = (className, parameters)
            
        actualClass = filename.split('_')[0]
        if predictedClassParameters[0] == actualClass:
            classesParametersHits[predictedClassParameters] += 1
            
    nHits = sum(classesParametersHits.values())
    nFiles = len(selectedFiles)
    hitRates = float(nHits)/nFiles
    
    return hitRates

def filterClasses(scenarios):
    classesParameters = []
    
    if isinstance(scenarios, tuple):
        classesParameters = list(scenarios)
    elif isinstance(scenarios, list):
        for scenario in scenarios:
            classesParameters += list(scenario)
            
    classesParameters = list(sorted(set(classesParameters)))
            
    classNames = []
    for className, parameters in classesParameters:
        if className not in classNames:
            classNames.append(className)
    
    return classNames

def filterParameter(scenario):
    parameters = scenario[0][1]
    return parameters

def filterParameters(scenarios):
    parameters = []
    for scenario in scenarios:
        for classname, parameter in scenario:
            parameters.append(parameter)
    
    parameters = list(sorted(set(parameters)))
    
    return parameters

def filterClassesParameters(scenarios):
    classesParameters = []
    for scenario in scenarios:
        classesParameters += list(scenario)
    
    classesParameters = list(sorted(set(classesParameters)))
    
    return classesParameters

def mountScenarios(bestScenarios):
    previousScenarios = bestScenarios.keys()
    classesParameters = filterClassesParameters(previousScenarios)
    
    newScenarios = []
    for scenario in previousScenarios:
        evaluatedClasses = filterClasses(scenario)
        for className, parameters in classesParameters:
            if className not in evaluatedClasses:
                newScenario = tuple(sorted(scenario + ((className, parameters),)))
                newScenarios.append(newScenario)
    
    newScenarios = list(sorted(set(newScenarios)))
    
    return newScenarios

def foundBestScenarios(newScenarios, hitRates, referenceRate):
    bestScenarios = OrderedDict()
    
    newScenarios = [p for _, p in list(sorted(zip(hitRates, newScenarios), reverse=True))]
    hitRates = list(sorted(hitRates, reverse=True))
    
    for key, value in enumerate(hitRates):
        if value >= referenceRate:
            bestScenarios[newScenarios[key]] = value
        else:
            break
    
    return bestScenarios

def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-data <input measures data file> --reference-rate <minimum accuracy desired> --rate-step <step of decreasing of the reference rate for scrap round> [--selected-measures <\'zip gzip bzip2 LZWHuffman entropy\'> --max-memory <maximum amount of memory to be used> --number-processes <number of parallel processes>]' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-data=', 'reference-rate=', 'rate-step=']
    optionalOptions = ['selected-measures=', 'max-memory=', 'number-processes=']
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
            measuresFilename = arg
            
            if os.path.isfile(measuresFilename):               
                folderPath = os.path.dirname(measuresFilename) + '/'
                
                print 'Opening measures data file'
                
                measuresFile = bz2.BZ2File(measuresFilename, 'rb')
                global measuresData
                measuresData = pickle.load(measuresFile)
                measuresFile.close()
                
                measuresEngines = getKeys(measuresData, 1)
                selectedMeasures = list(measuresEngines)
            else:
                print messagesColors.ERROR + 'Measures data file not found' + messagesColors.END
                sys.exit(2)
        elif opt == '--selected-measures':
            selectedMeasures = arg.split()
            
            for measure in selectedMeasures:
                if measure not in measuresEngines:
                    print messagesColors.ERROR + 'Enter a measure names among the possible ones: ' + str(measuresEngines) + messagesColors.END
                    sys.exit(2)
            
        elif opt == '--reference-rate':
            referenceRate = float(arg)
            
            if not 0 <= referenceRate <= 1:
                print messagesColors.ERROR + 'Enter a value for accuracy between 0 and 1' + messagesColors.END
                sys.exit(2)
        elif opt == '--rate-step':
            referenceRateStep = float(arg)
            
            if not 0 < referenceRateStep < 1:
                print messagesColors.ERROR + 'Enter a value for reference rate step greater than 0 and less than 1' + messagesColors.END
                sys.exit(2)
        elif opt == '--number-processes':
            nProcesses = int(arg)
            if nProcesses > multiprocessing.cpu_count():
                nProcesses = multiprocessing.cpu_count()
        elif opt == '--max-memory':
            maxMemory = float(arg)
            
            if not 0.5 <= maxMemory <= 1:
                print messagesColors.ERROR + 'Enter a value for maximum memory between 0.5 and 1' + messagesColors.END
                sys.exit(2)
                

    detailsFilename = folderPath + 'bestScenariosDetails.txt'
    executionDetails.environmentDetails(detailsFilename, lineOptions)
    executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
    
    pool = multiprocessing.Pool(nProcesses)
    memoryTotal = int(mem_info.meminfo()['MemTotal'].split()[0])
    memoryLimit = int(memoryTotal * maxMemory)
    
    parametersList = getKeys(measuresData, 0)
    filesList = getKeys(measuresData, 3)

    for measureEngine in selectedMeasures:
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '### Searching best classes and parameters for measure ' + measureEngine + ' ###' + messagesColors.END])
        
        classNames = getKeys(measuresData, 2)
        
        bestScenarios = OrderedDict()
        for className in classNames:
            for parameters in parametersList:
                bestScenarios[((className, parameters),)] = 1
        
        scrapRounds = []
        nClasses = 2
        while 2 <= nClasses <= len(classNames):
            startTime = time.time()
            executionDetails.outputDetails(detailsFilename, [messagesColors.SUBTITLE + '### Combining ' + str(nClasses) + ' classes ###' + messagesColors.END])
        
            executionDetails.outputDetails(detailsFilename, ['Combining parameters'])
            
            previousScenarios = bestScenarios.keys()
            classesParameters = filterClassesParameters(previousScenarios)
            
            nAuxFile = 0
            nCombinations = 0
            newScenarios = []
            for scenario in previousScenarios:
                evaluatedClasses = filterClasses(scenario)
                for className, parameters in classesParameters:
                    if className not in evaluatedClasses:
                        newScenario = tuple(sorted(scenario + ((className, parameters),)))
                        newScenarios.append(newScenario)
                    
                memoryAvailable = int(mem_info.meminfo()['MemAvailable'].split()[0])
                if memoryTotal - memoryAvailable > memoryLimit:
                    executionDetails.outputDetails(detailsFilename, [messagesColors.WARNING + 'WARNING: Processing temporary best scenarios in a external file due to the available low memory' + messagesColors.END])
                        
                    newScenarios = list(sorted(set(newScenarios)))
                    executionDetails.outputDetails(detailsFilename, ['Classifing images'])
                    hitRates = pool.map(partial(hitRate, filesList=filesList, measureEngine=measureEngine), newScenarios)
                    
                    bestScenarios = foundBestScenarios(newScenarios, hitRates, referenceRate)
                    
                    nCombinationsAux = len(newScenarios)
                    nCombinations += len(newScenarios)
                    
                    del newScenarios
                    del hitRates
                    
                    if len(bestScenarios) > 0:
                        nAuxFile += 1
                        
                        executionDetails.outputDetails(detailsFilename, ['Saving temporary external file #' + str(nAuxFile) + ' to ' + str(nCombinationsAux) + ' possibilities'])
                        bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(nClasses) + '_' + str(nAuxFile) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'wb')
                        pickle.dump(bestScenarios, bestScenariosAuxFile)
                        bestScenariosAuxFile.close()
                    
                    del bestScenarios
                    gc.collect()
                    newScenarios = []
                    
                    executionDetails.outputDetails(detailsFilename, ['Combining parameters'])
            
            if nAuxFile == 0:
                newScenarios = list(sorted(set(newScenarios)))
                
                executionDetails.outputDetails(detailsFilename, ['Classifing images'])
                hitRates = pool.map(partial(hitRate, filesList=filesList, measureEngine=measureEngine), newScenarios)
                
                bestScenarios = foundBestScenarios(newScenarios, hitRates, referenceRate)
                if len(bestScenarios) == 0 and len(newScenarios) > 0:
                    executionDetails.outputDetails(detailsFilename, [messagesColors.WARNING + 'Initiating validation below the reference rate' + messagesColors.END])
                    scrapRounds.append(nClasses)
                    
                    referenceRateAux = referenceRate
                    while len(filterClasses(bestScenarios.keys())) < len(classNames) and referenceRateAux > 0:
                        referenceRateAux -= referenceRateStep
                        bestScenarios = foundBestScenarios(newScenarios, hitRates, referenceRateAux)
                    
                    if len(bestScenarios) > 0:
                        referenceRateAux = min(bestScenarios.values())
                        executionDetails.outputDetails(detailsFilename, ['Best scenarios found above the reference rate ' + str(referenceRateAux)])
                
                nCombinations = len(newScenarios)
                
                if len(bestScenarios) > 0:
                    executionDetails.outputDetails(detailsFilename, ['Saving file of best round rates'])
                    bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(nClasses) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'wb')
                    pickle.dump(bestScenarios, bestScenariosAuxFile)
                    bestScenariosAuxFile.close()
                    
                    nClasses += 1
            else:
                if len(newScenarios) > 0:
                    newScenarios = list(sorted(set(newScenarios)))
                    executionDetails.outputDetails(detailsFilename, ['Classifing images'])
                    hitRates = pool.map(partial(hitRate, filesList=filesList, measureEngine=measureEngine), newScenarios)
                    
                    bestScenarios = foundBestScenarios(newScenarios, hitRates, referenceRate)
                    
                    nCombinations += len(newScenarios)
                else:
                    bestScenarios = OrderedDict()
                    
                for n in range(1, nAuxFile+1):
                    bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(nClasses) + '_' + str(n) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'rb')
                    bestScenariosAux = pickle.load(bestScenariosAuxFile)
                    bestScenariosAuxFile.close()
            
                    bestScenarios.update(bestScenariosAux)
                    
                bestScenarios = OrderedDict(sorted(bestScenarios.items()))
                
                executionDetails.outputDetails(detailsFilename, ['Saving file of best round rates'])
                bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(nClasses) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'wb')
                pickle.dump(bestScenarios, bestScenariosAuxFile)
                bestScenariosAuxFile.close()
                
                for n in range(1, nAuxFile+1):
                    os.remove(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(nClasses) + '_' + str(n) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2')
                
                nClasses += 1
            
            del newScenarios
            del hitRates
            gc.collect()
            
            nBestScenarios = len(bestScenarios)
                    
            executionDetails.outputDetails(detailsFilename, [str(nBestScenarios) + ' best scenarios found in to ' + str(nCombinations) + ' possibilities'])
            
            classNames = filterClasses(bestScenarios.keys())
                
            elapsedTime = executionDetails.calcTime(startTime, time.time())
            executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Elapsed time: ' + elapsedTime + messagesColors.END])
        
        executionDetails.outputDetails(detailsFilename, ['Saving file of best measure rates'])
        
        bestScenarios = OrderedDict()
        for n in range(2, nClasses):
            bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(n) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'rb')
            bestScenariosAux = pickle.load(bestScenariosAuxFile)
            bestScenariosAuxFile.close()
            
            nClassesStr = str(n) + ' classes'
            if n in scrapRounds:
                nClassesStr += '*'
            
            bestScenarios[nClassesStr] = bestScenariosAux
         
        bestClassesParametersFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'wb')
        pickle.dump(bestScenarios, bestClassesParametersFile)
        bestClassesParametersFile.close()
         
        for n in range(2, nClasses):
            os.remove(folderPath + 'bestScenariosAux_' + measureEngine + '_' + str(n) + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2')
    
    executionDetails.outputDetails(detailsFilename, ['Saving file of best scenarios'])
    
    bestScenarios = OrderedDict()
    for measureEngine in selectedMeasures:
        bestScenariosAuxFile = bz2.BZ2File(folderPath + 'bestScenariosAux_' + measureEngine + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2', 'rb')
        bestScenariosAux = pickle.load(bestScenariosAuxFile)
        bestScenariosAuxFile.close()
         
        bestScenarios[measureEngine] = bestScenariosAux
     
    bestClassesParametersFile = bz2.BZ2File(folderPath + 'bestScenarios.pckl.bz2', 'wb')
    pickle.dump(bestScenarios, bestClassesParametersFile)
    bestClassesParametersFile.close()
     
    for measureEngine in selectedMeasures:
        os.remove(folderPath + 'bestScenariosAux_' + measureEngine + '_' + os.path.basename(measuresFilename).split('.')[0] + '.pckl.bz2')
        
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    main(sys.argv[1:])