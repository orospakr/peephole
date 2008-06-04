import logging
import gobject

def virtual(func):
    """This is a decorator which can be used to mark functions
    as virtual. It will result in a warning being emitted
    when the function is used unless it is overridden.

    Mostly stolen from the Python Decorator library."""
    def newFunc(*args, **kwargs):
        logging.error("The driver function %s is not implemented." % func.__name__)
        #return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

class IdleObject(gobject.GObject):
    """
    Override gobject.GObject to always emit signals in the main thread
    by emmitting on an idle handler

    Cute hack by John Stowers <john.stowers@gmail.com>, under a permissive
    license.
    """
    def __init__(self):
        gobject.GObject.__init__(self)

    def emit(self, *args):
        gobject.idle_add(gobject.GObject.emit,self,*args)
