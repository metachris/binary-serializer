# Big-Endian ordering is used everywhere (for all bits in bytes, and for all 
# bytes in a byte-group (most significant comes first). 
#
# Varint means a byte array with the integer value encoded with base-128 varint 
#
# Todo
# ----
# [ ] decompressNumber always reverts into an int
#

def compressNumber(n):
    """
    Compress number into byte array by popping the most significant bytes if 
    empty. Start at the rightmost (least significant) byte and move to the left. 
    """
    if n == 0:
        return bytearray([0x00])
        
    result = bytearray()
    while n > 0:
        result.insert(0, n & 255)
        n >>= 8        
    return result

def decompressNumber(b):
    """
    Compress number into byte array by popping the most significant bytes if 
    empty. Start at the rightmost (least significant) byte and move to the left.
    
    int(b) will return a long value if the number uses more bytes:
        >>> type(int(1 << 62))
        <type 'int'>
        >>> type(int(1 << 63))
        <type 'long'>
        
    int() does not work well on a bytearray(b'\x00'), therefore only at the end
    """   
    result = 0
    round = 0
    for byte in b:
        round += 1
        if round > 1:
            result <<= 8
        result |= byte
    return result
    
def numberToVarint(n):
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

def varintToNumber(byteArray):
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
        
