import bincalc

function_mapper = {
    int: bincalc.decompressNumber,
    long: bincalc.decompressNumber
}

class BinaryDecoder:
    # final item dictionary. key:index, value:bytearray 
    items = {}
    
    # Blueprint 
    blueprint = None
    
    # map blueprint_str to items_index 
    items_blueprint_map = {} 
    
    # Temporary storage of raw request   
    byteArray = bytearray()
    
    def __init__(self):
        pass
    
    def __init__(self, blueprint):
        print "Blueprint:", blueprint
        self.loadBlueprint(blueprint)
    
    def loadBlueprint(self, blueprint):
        """ Map primitive functions to helper functions (decompressNumber, etc) """
        self.blueprint = {}
        for index in blueprint:
            function, key = blueprint[index]
            if function in function_mapper:
                function = function_mapper[function]            
            self.blueprint[index] = (function, key)
        
    def getVarlenInfo(self):
        """
        Pops self.byteArray from 0..n and extracts the current value.
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
           # If object blueprint available we can decode the bytearray now
           if self.blueprint:
               payload = self.blueprint[index][0](payload)
           self.items[index] = payload
           
        return self.items