def virtual(func):
    """This is a decorator which can be used to mark functions
    as virtual. It will result in a warning being emitted
    when the function is used unless it is overridden.

    Mostly stolen from the Python Decorator library."""
    def newFunc(*args, **kwargs):
        logging.error("The driver function %s is not implemented." % func.__name__,
                      category=DeprecationWarning)
        #return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc
