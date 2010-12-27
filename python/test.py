from encoder import BinaryEncoder
from decoder import BinaryDecoder
from bincalc import *
from example_blueprints import TestRequest

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
        
        e = BinaryDecoder(TestRequest)
        o = e.decode(x)
        
        print ">", o
       
        print "---\nComparing:"
        print " index |                  orig |                   restored | type "
        print " ------+-----------------------+----------------------------+----- "
        for key in test:
            print "   %3i |%22s |%27s | %s   " % (key, repr(test[key]), repr(o[key]), type(o[key]))
            self.assertTrue(test[key] == o[key])
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=3).run(suite)

    # printBits(numberToVarlenByteArray(16384))
