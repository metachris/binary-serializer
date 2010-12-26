package com.flockengine.serialization;

public class Test {
    private static void log(String s) { System.out.println(s); }
    private static void log(int s) { System.out.println(s); }
    private static void log(byte[] s) { System.out.println(s); }

    public static void main(String[] args) {        
        // Create 128 byte String
        String l = "";
        for (int i=0; i<128; i++)
            l += "a";
        
        // Build the package
        BinarySerializer bin = new BinarySerializer();
        bin.addString(127, l);
        bin.addString(128, "hello world");
        
        // Encode to final byte array
        byte[] result = bin.encode();
        log("result: " + result.length + " bytes");
        log ("===");
        
        // Decode payloads of request into indexed byte arrays
        bin.decode(result);

        log ("===");
        log(new String(bin.getBytes(127)));
    }
}