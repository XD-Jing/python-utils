# This code was taken and modified from Alex Martelli's
# "determine the name of the calling function" recipe (Thanks, Alex!)
#
# This code also benefits from a useful enhancement from Gary Robinson, allowing 
# only the arguments to __init__ to be copied, if that is desired.
#
# use sys._getframe() -- it returns a frame object, whose attribute
# f_locals is the list of local variables.  Before any processing goes on,
# will be the list of parameters passed in.
import sys

# By calling sys._getframe(1), you can get this information
# for the *caller* of the current function.  So you can package
# this functionality up into your own handy functions:
def initFromArgs(beingInitted, bJustArgs=False):
    codeObject = beingInitted.__class__.__init__.im_func.func_code
    for k,v in sys._getframe(1).f_locals.items():
        if k!='self' and ((not bJustArgs) or k in codeObject.co_varnames[1:codeObject.co_argcount]):
            setattr(beingInitted,k,v)
