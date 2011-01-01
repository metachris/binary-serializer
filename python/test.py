import random
import unittest

from encoder import BinaryEncoder
from decoder import BinaryDecoder
from example_blueprints import TestRequest
import bincalc

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_00_unicodeByteArray(self):
        tests = [u"asd", u"123", u"$#%", u"\u20ac", u"\u024B62"]
        for orig in tests:
            x = bincalc.unicodeToByteArray(orig)
            restored = bincalc.byteArrayToUnicode(x)
            # print repr(test), repr(x), repr(restored), restored
            self.assertEqual(orig, restored)
    
    def test_01_zigZag(self):
        test = [i for i in xrange(-1500, 1500)]
        for orig in test:
            z = bincalc.numberToZigZag(orig)
            restored = bincalc.zigZagToNumber(z)
            self.assertEqual(orig, restored)
            
    def test_02_numberToByteArray(self):
        # bincalc.py
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"

        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536, 1<<62, 1<<63]
        for orig in tests:
            b = bincalc.numberToBytes(orig)
            restored = bincalc.bytesToNumber(b)
            print "   %5i | %26s | %s" % (orig, repr(b), repr(restored))
            self.assertEqual(orig, restored)

    def test_03_numberToVarint(self):
        # bincalc.py
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"

        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536, 1<<62, 1<<63]
        for orig in tests:
            b = bincalc.numberToVarint(orig)
            restored = bincalc.varintToNumber(b)
            print "   %5i | %26s | %s" % (orig, repr(b), repr(restored))
            self.assertEqual(orig, restored)

    def test_10_encoder(self):
        # encoder.py + decoder.py
        test = {
            1: "hello world",
            7: u"test2\u20ac",
            9: 1<<63,
            128: 255,
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
            print "   %3i |%22s |%27s | %s   " % (key, test[key], o[key], type(o[key]))
            self.assertEqual(test[key], o[key])
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=3).run(suite)

    # printBits(numberToVarlenByteArray(16384))
