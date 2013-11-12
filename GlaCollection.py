class GlaCollection(list):

    def __init__(self, chain, prefix, vector_branch=""):
        self.chain = chain
        self.prefix = prefix
        #self.branch_list = self.GetListOfAttributes()
        
        if vector_branch:
            self.len = len(self.chain.__getattr__(self.prefix+vector_branch))
        else:
            self.len = self.chain.__getattr__(self.prefix+"n")

        self.MakeObjects()

    def MakeObjects(self):
        self.__delslice__(0,len(self))
        for iObj in range(self.len):
            self.append(GlaObject(self.chain, self.prefix, iObj))


class GlaObject:

    def __init__(self, event, prefix, index):
        self.event = event
        self.prefix = prefix
        self.index = index

    def __getattr__(self, property):
        return self.event.__getattr__(self.prefix+property)[self.index]
