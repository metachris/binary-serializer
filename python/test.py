from encoder import BinaryEncoder
from decoder import BinaryDecoder
from bincalc import *

import random
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.seq = range(10)

    def test_1_numberToByteArray(self):
        # bincalc.py
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"

        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536, 1<<62, 1<<63]
        for orig in tests:
            b = compressNumber(orig)
            restored = decompressNumber(b)
            print "   %5i | %26s | %s" % (orig, repr(b), repr(restored))
            self.assertTrue(orig == restored)

    def test_2_numberToVarint(self):
        # bincalc.py
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"
        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536, 1<<62, 1<<63]
        for orig in tests:
            b = numberToVarint(orig)
            restored = varintToNumber(b)
            print "   %5i | %26s | %s" % (orig, repr(b), repr(restored))
            self.assertTrue(orig == restored)

    def test_3_encoder(self):
        # encoder.py
        test = {
            1: "hello world",
            7: u"test2",
            9: 1<<63,
            128: 255
            #b.put(128, "a"*128)
        }
        
        print
        print "Testing:", repr(test)
        print "---\nEncoding:"
        b = BinaryEncoder()
        for key in test:
            b.put(key, test[key])
        x = b.encode()
        
        print ">", repr(x)        
        print "---\nRestoring:"
        
        e = BinaryDecoder()
        o = e.decode(x)
        
        print ">", o
       
        print "---\nComparing:"
        print " index |                  orig |                   restored | type "
        print " ------+-----------------------+----------------------------+----- "
        for key in test:
            restored = None
            if type(test[key]) in [str]:
                restored = str(o[key]) 
            elif type(test[key]) in [unicode]:
                restored = unicode(o[key]) 
            elif type(test[key]) in [int, long]:
                restored = decompressNumber(o[key]) 
            print "   %3i |%22s |%27s | %s   " % (key, repr(test[key]), repr(o[key]), type(restored))
            self.assertTrue(test[key] == restored)
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=3).run(suite)

    #unittest.main()
    exit(0)
    
    
    printBits(numberToVarlenByteArray(16384))
    exit(0)
    
    b = BinaryEncoder()
    b.put(1, "hello world")
    b.put(7, "test")
    b.put(9, 256)
    #b.put(128, "a"*128)
    x = b.encode()
    
    print repr(x)        
    print "---"
    
    e = BinaryDecoder()
    o = e.decode(x)
    print o
    #print int(o[9])
    exit(0)
    
    i = [0x00, 0x01, 0x02, 127, 128, 255, 256, 1024]
    
    for x in i:
        print "value:", x
        k = numberToVarlenByteArray(x)
        printBits(k)
        print "rev:", varlenByteArrayToNumber(k)
        print