from bincalc import printBits, numberToVarint, varintToNumber, numberToTrimmedByteArray, trimmedByteArrayToNumber

import random
import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.seq = range(10)

    def test_numberToByteArray(self):
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"

        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536]
        for i in tests:
            b = numberToTrimmedByteArray(i)
            o = trimmedByteArrayToNumber(b)
            print "   %5i | %26s | %s" % (i, repr(b), repr(o))
            self.assertTrue(i == o)

    def test_numberToVarint(self):
        print
        print "  number |                    encoded | restored"
        print "---------+----------------------------+----------"
        tests = [0, 1, 127, 128, 255, 256, 1024, 65535, 65536]
        for i in tests:
            b = numberToVarint(i)
            o = varintToNumber(b)
            print "   %5i | %26s | %s" % (i, repr(b), repr(o))
            self.assertTrue(i == o)
        
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