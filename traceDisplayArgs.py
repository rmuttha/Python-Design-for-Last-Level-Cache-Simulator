import sys
import os
import commonFunctions
from cache import *
from Global_variables import *

#data structure of cache
sets = []
for i in range(CACHE_SETS):
    lines = []
    for j in range(ASSOCIATIVITY):
        line = {'MESI':'00','tag':'0'}
        lines.append(line)
    set = {'PLRU':'0000000', 'lines': lines}
    sets.append(set)
cache = {'sets': sets}

argumentList = sys.argv[1:]
filename = argumentList[0]
mode = argumentList[1]

#check if trace file path exists or not
if  not (os.path.exists(filename)):
  print ("ERROR: file not readable or does not exist please check")
if mode in "-n":
  Normalmode = True
  print ("Running in Normal mode")
elif mode in "-s": 
  Normalmode = False
  print ("Running in Silent mode")
else:
  print ("Undefined mode")

#initializing counters 
cacheReadCount = 0
cacheWriteCount = 0
cacheHitCount = 0
cacheMissCount = 0

# function to decode incoming command to its respective events
def decodeCommand(cmd, cacheReadCount, cacheWriteCount):
  cpuRequest = ''
  snoopBusOp = ''
  clearCache = False
  printContents = False
  match cmd:
        case 0:
          cpuRequest = 'READ' 
          cacheReadCount = cacheReadCount + 1 
        case 1:
          cpuRequest = 'WRITE' 
          cacheWriteCount = cacheWriteCount + 1 
        case 2:
          cpuRequest = 'READ' 
          cacheReadCount = cacheReadCount + 1 
        case 3:
          snoopBusOp = 'INVALIDATE'
        case 4:
          snoopBusOp = 'READ'
        case 5:
          snoopBusOp = 'WRITE'
        case 6:
          snoopBusOp = 'RWIM'
        case 8:
          clearCache = True
        case 9:
          printContents = True
  return [cpuRequest, snoopBusOp, clearCache, printContents, cacheReadCount, cacheWriteCount]


#function to print statistics (cacahe read counts, write counts, hit counts and miss counts)
def printStatistics(cacheReadCount, cacheWriteCount, cacheHitCount, cacheMissCount):
  print("Number of cache reads", cacheReadCount)
  print("Number of cache writes", cacheWriteCount)
  print("Number of cache hits", cacheHitCount)
  print("Number of cache misses", cacheMissCount)
  cacheHitRatio = 0 if not (cacheHitCount + cacheMissCount) else cacheHitCount/(cacheHitCount + cacheMissCount)
  print("Cache hit ratio", cacheHitRatio)

hexString = '0123456789abcdefABCDEF'; 

f = open( filename, "r")
for line in f:
  #check is line in trace file is not empty
    if not line.isspace():
      [cmd, address] = line.split()
      #check if address is hex number or not
      ishex = all(c in hexString for c in address)
      if not ishex:
        print("ERROR: not a hexadecimal address")
      #check if command is less than 9
      elif int(cmd)>9:
        print("ERROR:invalid command")
      #check if address bits are more than 32  
      elif len(address)>8:  
        print("ERROR: address bits more than 32")
      else:     
        # print("Command is ",cmd)
        # print("Address is ", address)   
        [cpuRequest, snoopBusOp, clearCache, printContents, cacheReadCount, cacheWriteCount] = decodeCommand(int(cmd), cacheReadCount, cacheWriteCount)
        [tag, index, byteSelect] = commonFunctions.parseAddress(address)
        index = int(index, 2)
        set = cache['sets'][index]
        lines = set['lines']

        #for processor operations
        if(cpuRequest == 'READ' or cpuRequest == 'WRITE'):
            [updatedSet, cacheHitCount, cacheMissCount] = updateLine(tag, set, cpuRequest, snoopBusOp, cacheHitCount, cacheMissCount, address, Normalmode)
            cache['sets'][index] = updatedSet

          #for snooping operations
        elif(snoopBusOp == 'READ' or snoopBusOp == 'WRITE' or snoopBusOp == 'INVALIDATE' or snoopBusOp == 'RWIM'):
            tagMatchedWay = checkTag(tag, lines)
            if tagMatchedWay is not None:
              line = lines[tagMatchedWay]
              state = states(int(line['MESI'], 2))
              ourSnoopResult = commonFunctions.GetOurSnoopResult(state, lines, tag)
              [updatedLine, Message, BusOp, SnoopResult] = lineStatusUpdate(state, snoopBusOp, cpuRequest, line, address)
              resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult)
              cache['sets'][index]['lines'][tagMatchedWay] = updatedLine
            else:
              state = states.I
              Message = ''
              BusOp = ''
              SnoopResult = ''
              ourSnoopResult = commonFunctions.GetOurSnoopResult(state, lines, tag)
              resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult)
            # Clear cache
        elif clearCache:
            cache = commonFunctions.clearandreset(cache, states)
        elif printContents:
            commonFunctions.printcontent(cache)
      
    else :
      print("ERROR: empty line")


printStatistics(cacheReadCount, cacheWriteCount, cacheHitCount, cacheMissCount)  
f.close()
