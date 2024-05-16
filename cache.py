from Global_variables import *
from MESI import *
from pseudoLRU import *
import commonFunctions

def getEvictAddress(address, line):
    [tag, index, byteSelect] = commonFunctions.parseAddress(address)
    evictTag = line['tag']
    evictByteSelect = '000000' # to get the 32 bit address
    evictAddress = evictTag + index + evictByteSelect
    return hex(int(evictAddress, 2))

#function to update a line of the set for processor operations  
def updateLine(tag, set, cpuRequest, snoopBusOp, cacheHitCount, cacheMissCount, address, Normalmode):
    lines = set['lines']
    tagMatchedWay = checkTag(tag, lines)
    # print('tagMatchedWay', tagMatchedWay)
    if tagMatchedWay is not None:
        stateBits = lines[tagMatchedWay]['MESI']
        state = states(int(stateBits, 2))
        if (state != states.I):
            updatedSet = cacheHit(tag, tagMatchedWay, set, cpuRequest, snoopBusOp, address, Normalmode)
            cacheHitCount = cacheHitCount + 1
        else:
            updatedSet = cacheMiss(tag, set, cpuRequest, snoopBusOp, address, Normalmode)
            cacheMissCount = cacheMissCount + 1
    else:
        updatedSet = cacheMiss(tag, set, cpuRequest, snoopBusOp, address, Normalmode)
        cacheMissCount = cacheMissCount + 1
    return [updatedSet, cacheHitCount, cacheMissCount]

#function to handle cache miss 
def cacheMiss(tag, set, cpuRequest, snoopBusOp, address, Normalmode):
    lines = set['lines']
    LRUbits = [int(i) for i in list(set['PLRU'])]
    waysLength = len(lines)
    way = findWayToAccomodate(lines)
    # print('way', way)
    if way is not None:
        LRUbits = updateLRU(LRUbits, way, waysLength)
        set['PLRU'] = ''.join(str(x) for x in LRUbits)
        line = lines[way]
        state = states(int(line['MESI'], 2))
        ourSnoopResult = commonFunctions.GetOurSnoopResult(state, lines, tag)
        [updatedLine, Message, BusOp, SnoopResult] = lineStatusUpdate(state, snoopBusOp, cpuRequest, line, address)
        resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult)
        set['lines'][way]['MESI'] = updatedLine['MESI']
        set['lines'][way]['MESI'] = updatedLine['MESI']
        set['lines'][way]['tag'] = tag
    else:
        LRUWay = wayToReplace(LRUbits)
        LRUbits  = updateLRU(LRUbits, LRUWay, waysLength)
        set['PLRU'] = ''.join(str(x) for x in LRUbits)
        line = lines[LRUWay]
        state = states(int(line['MESI'], 2))
        evictAddress = getEvictAddress(address, line)
        if state == states.M:
            BusOp = 'WRITE'
            commonFunctions.BusOperation(BusOp, evictAddress, '', Normalmode) # Doesn't depend on SnoopResult
        Message = 'EVICTLINE' # do eviction address correctly
        commonFunctions.MessageToCache(Message, evictAddress, Normalmode)
        state = states.I # change state for newer coming line
        ourSnoopResult = commonFunctions.GetOurSnoopResult(state, lines, tag)
        [updatedLine, Message, BusOp, SnoopResult] = lineStatusUpdate(state, snoopBusOp, cpuRequest, line, address)
        resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult)
        set['lines'][LRUWay]['MESI'] = updatedLine['MESI']
        set['lines'][LRUWay]['tag'] = tag 
    return set


#function to handle cache hit
def cacheHit(tag, way, set, cpuRequest, snoopBusOp, address, Normalmode):
    lines = set['lines']
    LRUbits = [int(i) for i in list(set['PLRU'])]
    waysLength = len(lines)
    LRUbits = updateLRU(LRUbits, way, waysLength)
    set['PLRU'] = ''.join(str(x) for x in LRUbits)
    line = lines[way]
    state = states(int(line['MESI'], 2))
    ourSnoopResult = commonFunctions.GetOurSnoopResult(state, lines, tag)
    [updatedLine, Message, BusOp, SnoopResult] = lineStatusUpdate(state, snoopBusOp, cpuRequest, line, address)
    resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult)
    set['lines'][way]['MESI'] = updatedLine['MESI'] 
    return set


def findWayToAccomodate(lines):
    invalidWays = []
    for way in range(len(lines)):
        if states(int(lines[way]['MESI'], 2)) == states.I:
            invalidWays.append(way)
    way = min(invalidWays) if invalidWays else None 
    return way

def checkTag(tag, lines):
    for i in range(len(lines)):
        if (lines[i]['tag'] == tag):
         return i
    return None

