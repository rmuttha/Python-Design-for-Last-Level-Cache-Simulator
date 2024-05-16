from enum import Enum
import commonFunctions

class states(Enum):
    I = 0
    E = 1
    S = 2
    M = 3

def binToInt(binary):
    return int(binary, 2)

def intToBin(int):
    return '{0:02b}'.format(int)

# function to define MESI protocol
def stateUpdate(state, snoopBusOp, cpuReq, SnoopResult):
    nextState = ''
    if state is states.I and cpuReq == 'READ' and SnoopResult == 'NOHIT' :
        nextState = states.E
    elif state is states.I and cpuReq == 'READ' and (SnoopResult == 'HIT' or SnoopResult == 'HITM') :
        nextState = states.S
    elif state is states.I and cpuReq == 'WRITE':
        nextState = states.M
    elif state is states.E and cpuReq == 'WRITE':
        nextState = states.M
    elif state is states.S and cpuReq == 'WRITE':
        nextState = states.M

    #Transitions when snooping
    elif state is states.E and snoopBusOp == 'RWIM':
        nextState = states.I
    elif state is states.E and snoopBusOp == 'READ':
        nextState = states.S
    elif state is states.S and (snoopBusOp == 'RWIM' or snoopBusOp == 'INVALIDATE'):
        nextState = states.I
    elif state is states.M and snoopBusOp == 'RWIM':
        nextState = states.I
    elif state is states.M and snoopBusOp == 'READ':
        nextState = states.S
    else:
        nextState = state
    
    return nextState

def busOperationsUpdate(state, snoopBusOp, cpuReq):
    BusOp = ''
    #Bus operations for CPU Requests
    if state is states.I and cpuReq == 'READ':
        BusOp = 'READ'
    elif state is states.I and cpuReq == 'READ':
        BusOp = 'READ'
    elif state is states.I and cpuReq == 'WRITE':
        BusOp = 'RWIM'
    elif state is states.S and cpuReq == 'WRITE':
        BusOp = 'INVALIDATE'

    #Bus operations when snooping
    elif state is states.M and snoopBusOp == 'RWIM':
        BusOp = 'WRITE'
    elif state is states.M and snoopBusOp == 'READ':
        BusOp = 'WRITE'
    
    return BusOp

def updateMESIbits(nextState, line):
    line['MESI']=states(nextState).value
    return line

def updateTagbits(tag, line):
    line['tag']=tag
    return line

def updateLRUbits(LRUbits, set):
    set['PLRU']=LRUbits
    return set


def lineStatusUpdate(state, snoopBusOp, cpuRequest, line, address):
    SnoopResult = ''
    BusOp = busOperationsUpdate(state, snoopBusOp, cpuRequest)
    if (BusOp == 'READ' or BusOp == 'RWIM'):
        SnoopResult = commonFunctions.GetSnoopResult(address)
    nextState = stateUpdate(state, snoopBusOp, cpuRequest, SnoopResult)
    Message = commonFunctions.MessageToHigherCache(state, BusOp, snoopBusOp)
    # print(nextState)
    if(nextState != state):
        line['MESI'] = '{0:02b}'.format(states(nextState).value)
    return [line, Message, BusOp, SnoopResult]

    
def resultMessage(Message, address, BusOp, SnoopResult, snoopBusOp, Normalmode, ourSnoopResult):
    commonFunctions.MessageToCache(Message, address, Normalmode)
    commonFunctions.BusOperation(BusOp, address, SnoopResult, Normalmode)
    if (snoopBusOp == 'READ' or snoopBusOp == 'RWIM'):
        # print('ourSnoopResult', ourSnoopResult) #state is updated before getting ourSnoopResult
        commonFunctions.PutSnoopResult(address, ourSnoopResult, Normalmode)

