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
import os

sys.path.append('include')
import messagesColors
import executionDetails
import dictTools

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
    
def usage():
    print messagesColors.ERROR + 'Try ' + os.path.basename(os.path.realpath(__file__)) + ' --input-data <file with best scenarios>' + messagesColors.END
    sys.exit(2)
    
def main(argv):
    firstTime = time.time()
    
    requiredOptions = ['input-data=']
    optionalOptions = []
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
    
    for opt, arg in lineOptions:
        if opt == '--input-data':
            bestScenariosFilename = arg
            if os.path.isfile(bestScenariosFilename):
                print 'Opening best scenarios file'
                
                folderPath = os.path.dirname(bestScenariosFilename) + '/'
            
                bestScenariosFile = bz2.BZ2File(bestScenariosFilename, 'rb')
                bestScenariosData = pickle.load(bestScenariosFile)
                bestScenariosFile.close()
            else:
                print messagesColors.ERROR + 'Best scenarios file not found' + messagesColors.END
                sys.exit(2)
            
    detailsFilename = folderPath + 'reportBestScenarios.txt'
    executionDetails.environmentDetails(detailsFilename, lineOptions)
    executionDetails.outputDetails(detailsFilename, ['\nOUTPUT\n'])
    
    for metric in bestScenariosData.keys():
        executionDetails.outputDetails(detailsFilename, [messagesColors.TITLE + '############################## ' + metric + ' ##############################' + messagesColors.END])
        nClasses = bestScenariosData[metric].keys()
        
        for i, nClass in enumerate(nClasses):
            nClassesReference = None
            if '*' in nClass:
                nClassesReference = nClasses[i-1]
                break
        if nClassesReference == None:
            nClassesReference = nClasses[-1]
        
        for nClass in nClasses:
            executionDetails.outputDetails(detailsFilename, [messagesColors.SUBTITLE + '##### ' + nClass + ' #####' + messagesColors.END])
                                 
            totalScenarios = len(bestScenariosData[metric][nClass].keys())
                                                             
            maxHit = max(bestScenariosData[metric][nClass].values())
            maxScenarios = dictTools.getKeysByValue(bestScenariosData[metric][nClass], maxHit)
            nMaxScenarios = len(maxScenarios)
            
            decisionGroups = []
            for scenario in maxScenarios:
                classGroup = filterClasses(scenario)
                if classGroup not in decisionGroups:
                    decisionGroups.append(classGroup)
            nDecisisionGroups = len(decisionGroups)
            
            decisionClasses = filterClasses(maxScenarios)
            nDecisionClasses = len(decisionClasses)
            
            executionDetails.outputDetails(detailsFilename, ['Maximum accuracy: ' + str(maxHit)])
            executionDetails.outputDetails(detailsFilename, ['Possible classes (' + str(nDecisionClasses) + '):'])
            executionDetails.outputDetails(detailsFilename, [str(decisionClasses)])
            executionDetails.outputDetails(detailsFilename, ['Possible decision groups (' + str(nDecisisionGroups) + '):'])
            executionDetails.outputDetails(detailsFilename, [str(decisionGroups)])
            executionDetails.outputDetails(detailsFilename, ['Total best scenarios: ' + str(totalScenarios)])
            if nClass == nClassesReference or '*' in nClass:
                executionDetails.outputDetails(detailsFilename, ['Total max scenarios: ' + str(nMaxScenarios)])
                executionDetails.outputDetails(detailsFilename, ['Max scenarios:'])
                executionDetails.outputDetails(detailsFilename, [str(maxScenarios)])
            
            executionDetails.outputDetails(detailsFilename, [''])
        executionDetails.outputDetails(detailsFilename, [''])
        
    elapsedTime = executionDetails.calcTime(firstTime, time.time())
    executionDetails.outputDetails(detailsFilename, [messagesColors.SUCCESS + 'Total elapsed time: ' + elapsedTime + messagesColors.END])
    
if __name__ == '__main__':
    print messagesColors.WARNING + 'Executing ' + sys.argv[0] + ' with arguments ' + str(sys.argv[1:]) + messagesColors.END
    main(sys.argv[1:])