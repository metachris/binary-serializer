from encoder import BinaryEncoder
from decoder import BinaryDecoder
from bincalc import printBits, numberToVarlenByteArray, varlenByteArrayToNumber

#printBits(numberToVarlenByteArray("abc"))
#exit(0)

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