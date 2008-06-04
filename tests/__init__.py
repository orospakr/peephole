import logging
logging.basicConfig(level=logging.DEBUG)

import pmock

class CaptureConstraint(object):
    '''Allows you to retain an object that the pmock constraint receives
    for later prodding.'''

    def __init__(self, constraint, call_with_answer):
        self.constraint = constraint
        self.call_with_answer = call_with_answer

    def eval(self, arg_to_test):
        self.call_with_answer(arg_to_test)
        return self.constraint.eval(arg_to_test)

    def __repr__(self):
        return self.constraint.__repr__()

class SubscriptableMock(pmock.Mock):
    '''There was no way to create a pmock Mock that was
    subscriptable except by inheriting it.'''

    def setItems(self, items):
        self.my_items = items

    def __getitem__(self, pingas):
        try:
            return self.my_items[pingas]
        except TypeError:
            raise ValueError('The SubscriptableMock hasn\'t had its items set.')

    def len(self):
        return len(self.my_items)

def capture(arg_to_test, call_with_answer):
    return CaptureConstraint(arg_to_test, call_with_answer)


class BoundMethodConstraint(object):
    # HACK: this doesn't actually truly check to see if the method
    #       is a bound method, just that there is ANY method that
    #       has its name, which is good enough.

    def __init__(self, klass, method_name):
        self.klass = klass
        self.method_name = method_name

    def eval(self, bound_method_to_test):
        try:
            dir(self.klass).index(self.method_name)
            return True
        except ValueError:
            return False

    def __repr__(self):
        return "Expected a bound method named '%s', on an instance of '%s'" % (self.method_name, self.klass)

def bound_method(klass, method_name):
    return BoundMethodConstraint(klass, method_name)
