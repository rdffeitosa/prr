#!/usr/bin/python
# -*- coding: utf-8 -*-

#Adapted from
#Author: Imran
#Source: https://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys

from collections import OrderedDict

def flatten(dictData, parentKey=''):
    if isinstance(dictData, dict):
        flattenedDict = []
        for key, value in dictData.items():
            newKey = (parentKey) + (key,) if parentKey else (key,)
            if isinstance(value, dict):
                flattenedDict.extend(flatten(value, newKey).items())
            else:
                flattenedDict.append((newKey, value))
        
        return dict(flattenedDict)
    else:
        return None

###### End Author: Imran ######

def getKeys(dictData, level):
    nLevels = getLevels(dictData)
    if isinstance(dictData, dict) and nLevels > 0 and abs(level) <= nLevels:
        if level < 0:
            level = nLevels + level
            
        dictKeys = []
        
        flattenedDict = flatten(dictData)
        for key in flattenedDict.keys():
            try:
                dictKeys.append(key[level])
            except:
                pass
        
        dictKeys = list(sorted(set(dictKeys)))
        
        return dictKeys
    else:
        return None

def getLevels(dictData):
    if isinstance(dictData, dict):
        flattenedDict = flatten(dictData)
        nLevels = 0
        for key in flattenedDict.keys():
            if len(key) > nLevels:
                nLevels = len(key)
        
        return nLevels
    else:
        return None

def getKeysByValue(dictData, search):
    if isinstance(dictData, dict):
        foundKeys = []
        for key, value in dictData.items():
            if value == search:
                foundKeys.append(key)
        
        return foundKeys
    else:
        return None

def getValueByTuple(dictData, keyTuple):
    k = 0
    while k < len(keyTuple):
        try:
            dictData = dictData[keyTuple[k]]
            k += 1
        except:
            return None
        
    return dictData

def sortDict(dictData, mode, inverted=False):
    if mode == 'key':
        return OrderedDict(sorted(dictData.items(), key=lambda t: t[0], reverse=inverted))
    elif mode == 'value':
        return OrderedDict(sorted(dictData.items(), key=lambda t: t[1], reverse=inverted))
    else:
        return None