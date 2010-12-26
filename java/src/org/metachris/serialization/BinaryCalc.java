package com.flockengine.serialization;

public class BinaryCalc {
    private static void log(String s) { System.out.println(s); }
    
    /**
     * Length of an integer when compressed into a variable-length byte array
     * @param value
     * @return
     */
    public static final int varlenByteCount(int value) {
        int len = 0;
        while (value >>> ++len*7 > 0) ; 
        return len;
    }
    
    public static final byte[] createVarlenBytes(byte[] bytes) {
        return createVarlenBytes(bytes.length);
    }
    
    public static final byte[] createVarlenBytes(int value) {                
        //log("generating length-bytes for " + length + " bytes");
        
        int len_bytes = varlenByteCount(value); // number of length-bytes
        byte[] length_bytes = new byte[len_bytes]; // content of length-bytes
        byte cur_byte;
        
        // for each byte in the to-be-built length-bytes, get right 7 bits and add to total
        for (int i=0; i<len_bytes; i++) {
            cur_byte = 0;
            
            // Get rightmost 7 bits
            cur_byte = (byte) (value & (~0 >>> (32 - 7))); // last (right) part gets a 0 as leftmost bit (last length byte)
            
            // remove the currently used bits from the number of payload bytes
            value >>>= 7;
        
            // all further (left) bytes get a 1 as leftmost bit, because more length-bytes are following
            if (i > 0) {
                cur_byte |= 128; // set left bit of this byte to 1
            }
        
            length_bytes[(len_bytes-1)-i] = cur_byte;
        }
        
        return length_bytes;
    }
}
