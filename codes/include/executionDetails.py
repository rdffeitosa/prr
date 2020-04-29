#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import platform
import cpu_info
import mem_info
import string

def environmentDetails(detailsFilename, parameters):
    cpuinfo = cpu_info.cpuinfo()
    meminfo = mem_info.meminfo()
    system = ' '.join(platform.linux_distribution())
    cpu = cpuinfo[cpuinfo.keys()[0]]['model name']
    memory = format(meminfo['MemTotal'])
    
    detailsFile = open(detailsFilename, 'a+')
    
    detailsFile.write('ENVIRONMENT\n')
    detailsFile.write(system + '\n')
    detailsFile.write(cpu + '\n')
    detailsFile.write(memory + '\n')
    
    detailsFile.write('\nPARAMETERS\n')
    for parameter in parameters:
        detailsFile.write(parameter[0] + ' = ' + parameter[1] + '\n')
    
    detailsFile.close()

def outputDetails(detailsFilename, outputs):
    colors = ['\033[96m', '\033[94m', '\033[35m', '\033[31m', '\033[33m', '\033[32m', '\x1b[6;30;42m', '\033[0m']
    
    detailsFile = open(detailsFilename, 'a+')
    
    for output in outputs:
        print output
        for color in colors:
            output = string.replace(output, color, '')
        detailsFile.write(output + '\n')
    
    detailsFile.close()

def calcTime(startTime, finalTime):
    diffTime = finalTime - startTime
    minutes, seconds = divmod(diffTime, 60)
    hours, minutes = divmod(minutes, 60)
    
    return str(int(hours)).zfill(2) + ':' + str(int(minutes)).zfill(2) + ':' + str(int(seconds)).zfill(2)