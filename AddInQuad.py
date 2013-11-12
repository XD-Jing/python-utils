import math

def AddInQuad(list):

    return math.sqrt(reduce(lambda x,y: x+y*y, list, 0))
