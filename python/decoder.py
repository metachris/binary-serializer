from bincalc import printBits, numberToVarlenByteArray, varlenByteArrayToNumber
        
class BinaryDecoder:
    items = {} # key:index
    byteArray = bytearray()
    
    def __init__(self):
        pass
 
    def getVarlenInfo(self):
        """
        Parses self.byteArray from 0..n and extracts the current
        value.
        """
        number = 0
        round = 0
        while True:
            round += 1
            if round > 1:
                number <<= 7 

            cur_byte = self.byteArray.pop(0)            
            if cur_byte >> 7 == 1:
                number |= cur_byte & 127 # remove length-info bit
            else:
                # last length byte. append and exit
                number |= cur_byte
                break
                
        return number            
    
    def decode(self, byteArray):
        """
        Decodes a given request in form of a bytearray, and
        extracts the content into a dictionary mapped to the 
        original index keys.
        """
        self.items = {}
        self.byteArray = byteArray
        self.byteArray.pop(0) # request start byte 0x00
        
        while len(self.byteArray) > 0:
           payload_length = self.getVarlenInfo()
           index = self.getVarlenInfo()
           payload = self.byteArray[:payload_length]
           self.byteArray[:payload_length] = []
           self.items[index] = payload
           
        return self.items