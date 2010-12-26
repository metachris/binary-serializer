from bincalc import printBits, numberToVarlenByteArray, varlenByteArrayToNumber, numberToByteArray

class BinaryEncoder:
    items = {} # key:int, value:bytearray
    
    def __init__(self):
        pass
    
    def put(self, index, value):
        if type(value) == int or type(value) == long:
            self.items[index] = numberToByteArray(value)
            print repr(self.items[index])
        else:
            self.items[index] = bytearray(value)
        
    def encode(self):
        """ Returns a single byte array including all the payloads and indexes"""
        print "encoding"
        result = bytearray()
        result.append(0x00)
        
        for index in self.items:
            item = self.items[index]
            print "-", index, "\t>", repr(item)
            
            # append length bytes
            result.extend(numberToVarlenByteArray(len(item)))
            
            # append index bytes
            result.extend(numberToVarlenByteArray(index))
            
            # append content bytes
            result.extend(item)
        
        return result
        