from array import array

def packet_fixture(packet_array):
    '''Pass this an array of 8-bit integers to make a
    string out of them.  Great for representing packet
    fixtures textually in the testcase.'''
    return (array('B', packet_array).tostring())
