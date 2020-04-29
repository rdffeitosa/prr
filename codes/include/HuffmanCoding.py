#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

from heapq import heappush, heappop, heapify

def frequencyDictionary(rawData_):
    colorHistogram = {}
    
    for colorValue in rawData_:
        if colorValue not in colorHistogram:
            colorHistogram[colorValue] = 0
        colorHistogram[colorValue] += 1
    
    return colorHistogram
 
def huffmanEncoding(colorHistogram):
    dataHeap = [[colorFrequency, [colorValue, ""]] for colorValue, colorFrequency in colorHistogram.items()]
    heapify(dataHeap)
    
    while len(dataHeap) > 1:
        leftNode = heappop(dataHeap)
        rightNode = heappop(dataHeap)
        
        for node in leftNode[1:]:
            node[1] = '0' + node[1]
            
        for node in rightNode[1:]:
            node[1] = '1' + node[1]
            
        heappush(dataHeap, [leftNode[0] + rightNode[0]] + leftNode[1:] + rightNode[1:])
        
    huffmanTable = sorted(heappop(dataHeap)[1:], key=lambda p:(len(p[1]), p))
    huffmanDict_ = {valueCoding[0]:valueCoding[1] for valueCoding in huffmanTable}
    
    return huffmanDict_

def dataCompressing(rawData_):
    colorHistogram = frequencyDictionary(rawData_)
    huffmanDict_ = huffmanEncoding(colorHistogram)
    
    compressedString = []
    for colorValue in rawData_:
        compressedString.append(huffmanDict_[colorValue])
        
    compressedString = ''.join(compressedString)
    
    return compressedString, huffmanDict_

def dataDecompressing(compressedData_, huffmanDict_):
    decompressedData_ = []
    currentCode = ""
    
    for bit in compressedData_:
        currentCode += bit
        if currentCode in huffmanDict_.values():
            colorValue = list(huffmanDict_.keys())[list(huffmanDict_.values()).index(currentCode)]
            decompressedData_.append(colorValue)
            currentCode = ""
    
    return decompressedData_