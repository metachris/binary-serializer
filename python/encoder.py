#
# BinaryEncoder
#
# Currently supported data types:
#   int, long, str, unicode, bytearray
#
# Todo:
#   - negative numbers
#   - float, complex
#

from bincalc import *

class BinaryEncoder:
    items = {} # key:int, value:bytearray        
    
    def put(self, index, value):
        if type(value) == int or type(value) == long:
            self.items[index] = compressNumber(value)
        elif type(value) == bytearray or type(value) == str:
            self.items[index] = bytearray(value)
        elif type(value) == unicode:
            self.items[index] = bytearray(value.encode("utf-8"))            
        else:
            raise NotImplementedError("Type %s not supported" % type(value))
        
    def encode(self):
        """ Returns a single byte array including all the payloads and indexes"""
        result = bytearray()
        result.append(0x00)
        
        for index in self.items:
            item = self.items[index]
            print "-", index, "\t>", repr(item)
            
            # append length bytes
            result.extend(numberToVarint(len(item)))
            
            # append index bytes
            result.extend(numberToVarint(index))
            
            # append content bytes
            result.extend(item)
        
        return result
        