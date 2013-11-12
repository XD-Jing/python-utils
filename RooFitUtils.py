
class RooArgSetIter:
    def __init__(self, ras):
        self.ras = ras
        self.iter = ras.iterator()
    def __iter__(self):
        return self
    def next(self):
        obj = self.iter.Next()
        if not obj:
            raise StopIteration
        else:
            return obj
