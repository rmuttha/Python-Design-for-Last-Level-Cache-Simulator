from Global_variables import *
import MESI  
import cache 
#function to Simulate the reporting of snoop results by other caches
def GetSnoopResult(address):
    address = int(address, 16)
    if address % 4 == 0:
        snoopResult = 'HIT'
    elif address % 4  == 1:
        snoopResult = 'HITM'
    else: snoopResult =  'NOHIT'  
   
    return snoopResult


#function to report a bus operation and to capture the snoop results of last level 
#caches of other processors
def  BusOperation(BusOp,Address,SnoopResult, Normalmode):
    if (Normalmode):
        print("BusOp:", BusOp, "Address:", Address, "Snoop Result:", SnoopResult)

#function to Report the result of our snooping bus operations performed by other caches
def  PutSnoopResult(Address,SnoopResult, Normalmode):
    if (Normalmode):
        print("Address:", Address, "SnoopResult:", SnoopResult)

#function to simulate communication to our upper level cache
def MessageToCache(Message, Address, Normalmode):
    if (Normalmode):
        print("L2:", Message, "Address:", Address, "\n")

#function to clear cache and reset all the states
def clearandreset(cache, states):
    for set in range(CACHE_SETS):
        for line in range(ASSOCIATIVITY):
            #cache['sets'][set]['lines'][line]['tag'] = 0
            cache['sets'][set]['lines'][line]['MESI'] = '{0:02b}'.format(states.I.value)
    return cache

#function to print contents and state of each valid cache line (doesn’t end simulation!)
def printcontent(cache):
    for index in range(CACHE_SETS):
        for line in range(ASSOCIATIVITY):
            stateBits = cache['sets'][index]['lines'][line]['MESI']
            state = MESI.states(int(stateBits, 2))
            pLRUbits = cache['sets'][index]['PLRU']
            
            if state != MESI.states.I:
                print('set:', index, 'pLRU:',pLRUbits, 'line:', line,'MESI:',state,'tag:',cache['sets'][index]['lines'][line]['tag'])
    # return

#function to return snoop result of our caache 
def GetOurSnoopResult(state, lines, tag):
    tagMatchedWay = cache.checkTag(tag, lines)
    if tagMatchedWay is not None:
        if state == MESI.states.I:
            ourSnoopResult = 'NOHIT'
        elif (state == MESI.states.E) or (state == MESI.states.S):
            ourSnoopResult = 'HIT'
        else:
            ourSnoopResult = 'HITM'
    else:
        ourSnoopResult = 'NOHIT'
    return ourSnoopResult    

# function to generate message to Higher cache 
def MessageToHigherCache(state, BusOp, snoopBusOp):
    Message = ''
    if BusOp == 'READ' or BusOp == 'RWIM':
        Message = 'SENDLINE'
    elif state is MESI.states.M  and snoopBusOp == 'RWIM':
        Message = 'GETLINE' + ' & ' + 'INVALIDATELINE'
    elif BusOp == 'WRITE':
        Message = 'GETLINE'
    elif snoopBusOp == 'RWIM' or snoopBusOp == 'INVALIDATE':
        Message = 'INVALIDATELINE'
    elif state is MESI.states.M  and snoopBusOp == 'READ':
        Message = 'GETLINE'
    return Message

#function to parse the address 
def parseAddress(addr):
        addr = "{0:032b}".format(int(addr, 16))
        tag = addr[0:11]
        index = addr[11:26]
        byteSelect = addr[26:32]
        return [tag, index, byteSelect] 

