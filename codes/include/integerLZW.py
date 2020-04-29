#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@author: Rafael Divino Ferreira Feitosa (rdffeitosa@gmail.com)
'''

import math
import struct
import listTools

def dataCompressing(compressingDictionary_, rawData_):
    compressingDictionary_ = dict(compressingDictionary_)
    dataLength = len(rawData_)
    compressedData_ = []
    
    i = 0
    currentValue = rawData_[i]
    
    while i < dataLength-1:
        lastKey = compressingDictionary_.keys()[-1]
        nextValue = rawData_[i+1]
        
        currentEntry = list(listTools.flatten([currentValue, nextValue]))
        
        if currentEntry in compressingDictionary_.values():
            currentValue = currentEntry
        else:
            dictionaryKey = compressingDictionary_.keys()[compressingDictionary_.values().index(currentValue)]
            compressedData_.append(dictionaryKey)
            compressingDictionary_[lastKey+1] = currentEntry
            currentValue = nextValue
            
        i += 1
                
    dictionaryKey = compressingDictionary_.keys()[compressingDictionary_.values().index(currentValue)]
    compressedData_.append(dictionaryKey)
    
    return compressedData_

def writeStream(compressedData_, filePath_):
    dictionaryLength = max(compressedData_)
    nBits = int(math.floor(math.log(dictionaryLength) / math.log(2) ) + 1)
    
    compressedFile = open(filePath_,'wb')
    encodedValue = struct.pack("<B", nBits)
    compressedFile.write(encodedValue)
    streamBuffer = ""

    for pointer in compressedData_:
        bitsString = bin(pointer)[2:].zfill(nBits)
        streamBuffer += bitsString
        while len(streamBuffer) >= 8:
            encodedValue = struct.pack("<B", int(streamBuffer[:8],2))
            compressedFile.write(encodedValue)
            streamBuffer = streamBuffer[8:]
    
    if len(streamBuffer) > 0:
        encodedValue = struct.pack("<B", int(streamBuffer,2))
        compressedFile.write(encodedValue)
    
    compressedFile.close()
    
def readStream(filePath):
    streamBuffer = ""
    nPointerBits = 0
    pointersData_ = []
    with open(filePath,'rb') as compressedData_:
        actualByte = compressedData_.read(1)
        
        while actualByte != "":
            if nPointerBits > 0:
                encodedByte = actualByte.encode('hex')
                
                bitString = bin(int(encodedByte, 16))[2:].zfill(8)
                
                if nextByte == "":
                    dropBits = 8 + len(streamBuffer) - nPointerBits
                    bitString = bitString[dropBits:]
                else:
                    compressedData_.seek(-1, 1)
                    
                streamBuffer += bitString
        
                while len(streamBuffer) >= nPointerBits:
                    bitString = streamBuffer[:nPointerBits]
                    pointer = int(bitString, 2)
                    pointersData_.append(pointer)
                    streamBuffer = streamBuffer[nPointerBits:]
            else:
                nPointerBits = struct.unpack("<B", actualByte)[0]
            
            actualByte = compressedData_.read(1)
            nextByte = compressedData_.read(1)
    
    compressedData_.close()
    
    return pointersData_
    

def dataDecompressing(compressingDictionary_, compressedData_):
    decompressedData_ = []
    
    priorPointer = compressedData_.pop(0)
    decompressedData_.append(compressingDictionary_[priorPointer])
    for nextPointer in compressedData_:
        lastKey = compressingDictionary_.keys()[-1]

        if nextPointer not in compressingDictionary_.keys():
            newEntry = list(listTools.flatten([compressingDictionary_[priorPointer], list(listTools.flatten(compressingDictionary_[priorPointer]))[0]]))
            decompressedData_ += newEntry
        else:
            newEntry = list(listTools.flatten([compressingDictionary_[priorPointer], list(listTools.flatten(compressingDictionary_[nextPointer]))[0]]))
            decompressedData_ += list(listTools.flatten(compressingDictionary_[nextPointer]))
        
        compressingDictionary_[lastKey+1] = newEntry
        priorPointer = nextPointer
        
    return decompressedData_