
def updateLRU(LRUbits, way, waysLength):
    tree = createTree(LRUbits, 0, len(LRUbits))
    updatedTree = updateNode(tree, way, waysLength)
    LRUbits = traverse(updatedTree)
    return LRUbits

D, L, R = 'data', 'left', 'right'

def updateNode(tree, way, reducedWay):
        if reducedWay == 1:
            return tree
        elif way < reducedWay/2:
            tree[D] = 0
            tree[L] = updateNode(tree[L], way, reducedWay/2)
        else:
           tree[D] = 1
           tree[R] = updateNode(tree[R], way - reducedWay/2, reducedWay/2) 
        return tree

def traverse(tree):
        
        Treebits = []
        if tree is None:
            return Treebits
        queue = [tree] 
        while len(queue) > 0:
            # print(queue)
            currNode = queue.pop(0)
            # print(currNode[D])
            Treebits.append(currNode[D])

            if currNode[L] is not None:
                queue.append(currNode[L])

            if currNode[R] is not None:
                queue.append(currNode[R])

        return Treebits

def createTree(LRUbits, i, n):
    tree = None
    if i<n:
        tree = {D: LRUbits[i], L: None, R: None}
        tree[L] = createTree(LRUbits, 2*i + 1, n)
        tree[R] = createTree(LRUbits, 2*i + 2, n)
    return tree   

def findWayIndex(wayBits):
    binaryString = ''.join(str(x) for x in wayBits)
    n = len(binaryString)
    onesComplement = ""

    for i in range(n):
        onesComplement += flip(binaryString[i])
    wayIndex = int(onesComplement, 2)
    return wayIndex

def wayToReplace(LRUbits):
        tree = createTree(LRUbits, 0, len(LRUbits))
        wayBits = []
        if tree is None:
            return -1
        queue = [tree] 
        while queue != [None]:
            # print(queue)
            # print(wayBits)
            currNode = queue.pop(0)
            # print(currNode)
            wayBits.append(currNode[D])
            if currNode[D]:
                queue.append(currNode[L])
            else:
                queue.append(currNode[R])

        return findWayIndex(wayBits)
    

def flip(c):
    return '1' if (c == '0') else '0'

waysLength = 8 # scalable LRU implementation
LRUbits = [0]*7
LRUtree = (createTree(LRUbits, 0, len(LRUbits)))

LRUbits = updateLRU(LRUbits, 0, waysLength)
LRUbits = updateLRU(LRUbits, 1, waysLength)
LRUbits = updateLRU(LRUbits, 2, waysLength)
LRUbits = updateLRU(LRUbits, 3, waysLength)
LRUbits = updateLRU(LRUbits, 4, waysLength)
LRUbits = updateLRU(LRUbits, 5, waysLength)
LRUbits = updateLRU(LRUbits, 6, waysLength)
LRUbits = updateLRU(LRUbits, 7, waysLength)
LRUbits = updateLRU(LRUbits, 0, waysLength)
LRUbits = updateLRU(LRUbits, 1, waysLength)
LRUbits = updateLRU(LRUbits, 2, waysLength)
LRUbits = updateLRU(LRUbits, 3, waysLength)

# print(tree)
# LRUbits = traverse(tree)
# print(LRUbits)
# LRUbits = [0] * 8
wayBits = wayToReplace(LRUbits)
# print(wayBits)
# emptyList = [None]*7

# print((createTree(emptyList, 0, len(emptyList) )) is None)



