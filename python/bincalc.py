def numberToVarlenByteArray(n):
    """ 
    Converts a number into a variable length byte array (using 7 bits per
    byte, big endian encoding, highest bit is info if last length-byte (0) or 
    not (1)). 
    
    Start at the lower byte (right) and work the way up :)    
    """
    value = int(n)
    if value == 0:
        return bytearray([0x00])
        
    result = bytearray()    
    round = 0
    while value > 0:
        # only use the lower 7 bits of this byte (big endian)
        # if subsequent length byte, set highest bit to 1, else just insert the value with 
        result.insert(0, value & 127 | 128 if round > 0 else value & 127) # sets length-bit to 1 on all but first
        value >>= 7
        round += 1
    return result

def varlenByteArrayToNumber(byteArray):
    """
    Converts a varlen bytearray back into a normal number, basically only
    pushing the last 7 bits of each varlen byte onto the result value
    """
    number = 0
    round = 0
    for byte in byteArray:
        round += 1
        if round > 1:
            number <<= 7
        number |= byte & 127 # only use the lower 7 bits of this byte (big endian)
    return number        
    
def printBits(byteArray):
    # Print all bits of this bytearray
    print repr(byteArray)
    for byte in byteArray:
        c1 = "%3i | " % byte
        c2 = ""
        for _ in xrange(8):
            c2 = "%s%s" % ("1" if byte & 1 else "0", c2)
            byte >>= 1 
        print "%s%s" % (c1, c2)
        
def numberToByteArray(n):
    """
    Convert number into byte array. Start at the rightmost byte
    and go to the left.
    """
    result = bytearray()
    while n > 0:
        result.insert(0, n & 255)
        n >>= 8        
    return result