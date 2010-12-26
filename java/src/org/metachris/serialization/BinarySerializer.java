package com.flockengine.serialization;

import java.util.HashMap;

/**
 * Minimal Binary Serializer 
 * 
 * Request-Start:      0x00
 * Foreach payload:
 *   - length-byte(s): variable 
 *   - index-byte(s):  variable
 *   - content-bytes:  variable
 * 
 * @author chris
 *
 */

public class BinarySerializer {
    private HashMap<Integer, byte[]> items;
    
    private static void log(String s) { System.out.println(s); }
    private static void log(int i) { System.out.println(i); }

    public BinarySerializer() {
        items = new HashMap<Integer, byte[]>();
    }
    
    /* --------------------------------------------- */
    /* ------------- Adding Payloads --------------- */
    /* --------------------------------------------- */
    public BinarySerializer addBytes(int index, byte[] payload) {
        items.put(index, payload); 
        return this;
    }
    
    public BinarySerializer addString(int index, String payload) {
        return addBytes(index, payload.getBytes());
    }
    
    /* --------------------------------------------- */
    /* ------------- Returning Payloads ------------ */
    /* --------------------------------------------- */
    public byte[] getBytes(int index) {
        return items.get(index);
    }

    public String getString(int index) {
        return new String(items.get(index));
    }

    /* --------------------------------------------- */
    /* ------------- Compiling Request ------------- */
    /* --------------------------------------------- */
    public byte[] encode() {
        // number of length bytes for this content
        int len = 1; // 0x00 request start byte

        // Get length of final parcel by traversing all payloads
        for (int index : items.keySet()) {
            len += BinaryCalc.varlenByteCount(items.get(index).length);
            len += BinaryCalc.varlenByteCount(index);
            len += items.get(index).length; 
        }
        
        int i;
        byte[] len_bytes;
        byte[] index_bytes;
        byte[] item;

        byte[] out = new byte[len];
        out[0] = 0x00; // request start byte
        int pos = 1;   // current position in out array
        
        for (int index : items.keySet()) {
            item = items.get(index);
            len_bytes = BinaryCalc.createVarlenBytes(item);
            index_bytes = BinaryCalc.createVarlenBytes(index);

            log("index:       " + index);
            log("index-bytes: " + index_bytes.length);
            log("content      " + new String(items.get(index)));
            log("content-len: " + items.get(index).length);
            log("len-bytes2:  " + len_bytes.length);
            log("----");

            for (i=0; i<len_bytes.length; i++) 
                out[pos++] = len_bytes[i];
            for (i=0; i<index_bytes.length; i++) 
                out[pos++] = index_bytes[i];
            for (i=0; i<item.length; i++) 
                out[pos++] = item[i];
        }

        log("total length: " + len);
        log("last pos: " + pos);
        return out;
    }
    
    public void decode(byte[] request) {
        items = new HashMap<Integer, byte[]>();
        
        byte cur_byte;
        int payload_index;
        int payload_length;
        byte[] payload_content;
        boolean isLastLengthByte;
        
        int pos = 1;
        while (pos < request.length) {
            // read length byte(s)
            payload_length = 0;
            isLastLengthByte = false;            
            while (!isLastLengthByte) {
                // 1. get current length-byte
                cur_byte = request[pos++];
                
                // 2. check if last or not (leftmost bit == 1 - makes a negative number with signed bytes)
                if ((cur_byte & 128) == 128) {
                    // not last. set left bit to 0
                    cur_byte &= ~128;
                    
                    // Add the 7 bits of the current length-byte to the payload_length, and shift it to the right for next one
                    payload_length |= cur_byte;
                    payload_length <<= 7;
                } else {
                    // 3. add last length-byte (which has left bit set to 0)
                    payload_length |= cur_byte;             
                    isLastLengthByte = true;
                }
            }            
            log("payload length=" + payload_length);
            
            // read index byte(s)
            isLastLengthByte = false;
            payload_index = 0;
            while (!isLastLengthByte) {
                // 1. get current length-byte
                cur_byte = request[pos++];
                
                // 2. check if last or not (leftmost bit == 1 - makes a negative number with signed bytes)
                if ((cur_byte & 128) == 128) {
                    // not last. set left bit to 0
                    cur_byte &= ~128;
                    
                    // Add the 7 bits of the current length-byte to the payload_length, and shift it to the right for next one
                    payload_index |= cur_byte;
                    payload_index <<= 7;
                } else {
                    // 3. add last length-byte (which has left bit set to 0)
                    payload_index |= cur_byte;             
                    isLastLengthByte = true;
                }
            }
            log("index=" + payload_index);
            
            // read payload byte(s)
            payload_content = new byte[payload_length];
            for (int i=0; i<payload_length; i++)
                payload_content[i] = request[pos++];
            
            log("payload: " + new String(payload_content));
            items.put(payload_index, payload_content);
        }
    }
}