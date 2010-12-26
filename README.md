Overview
========

Binary Serializer provides a leightweight binary serialization protocol and 
methods for encoding and decoding. One request can contain multiple payloads
and the output is a binary request with minimal serialization overhead.

The serialization works similar to Protocol Buffers [1], using a variable
amount of length-bytes indicating the number of bytes to read for the next
payload. 

Where this project differs from protobuf is that it provides only the 
binary serialization functionality, without object boilerplates used to 
decode a request into a ready-to-use object. This projects accesses the 
payloads by integers [0..n], eg. request.put(index, "first payload"); and 
request.getString(index);

Furthermore this serialization protocol provides a way to separate multiple 
stacked requests, where multiple requests arrive at once when reading from
a socket (often happens with mobile devices when sending many requests in 
a short time).

[1] http://code.google.com/p/protobuf/

-----
 
Goals
-----
* Most efficient, binary protocol serialization

Non-Goals
---------
* Object "blueprints" a la protocol buffers, which can be used to decode
  a request into a ready-to-use object. Access to values is only provided
  via integer keys.


-----

Protocol Overview
=================

    Byte # | Value | Explanation
    
    -------- Request Start --------------------------
         0 | 0x00  | start of new request identifyer
         
    -------- For each payload -----------------------
         1 | 0x01  | length-byte(s) (1..n bytes) 
         2 | 0x01  | index-byte(s)  (1..n bytes)
      3..n | ...   | payload-bytes  (1..n bytes) 
     
There can never be a length-byte with the value 0, because an empty payload
(with 0 bytes) would not be serialized.
     
Length and Index Bytes
----------------------
Length and index bytes prepend any payload and work the same way: 
The length-byte indicates the payload's length in bytes. One length-
byte uses 7 bits to indicate the length, and the 8th (highest) bit is used to 
indicate whether this is the last length-byte (0) or if the next byte is also
a length byte (1). Big-endian is used (the highest-value bit is the left one,
the lowest value bit is right one):

    Bit Values: [ x | 64 | 32 | 16 | 8 | 4 | 2 | 1 ]
                  | 
                  + last-length-byte indicator (0=last, 1=next-also-length-byte)
  

Since each length-byte uses only 7 bits for the payload length the following
limits arise:
  
    One length-byte:  7 bits   = 2^7  = 0..127 payload bytes max
    Two length-bytes: 2*7 bits = 2^14 = 0..16383 payload bytes max 

A payload with 18384 bytes would generate a third length-byte.


    Payload-length  |  [  length byte 0  ] | [  length byte 1  ]
    ----------------+----------------------+----------------------  
    1 byte          |  [ 0 0 0 0 0 0 0 1 ] |
    127 bytes       |  [ 0 1 1 1 1 1 1 1 ] |                         
    128 bytes       |  [ 1 0 0 0 0 0 0 1 ] | [ 0 0 0 0 0 0 0 0 ]  
    255 bytes       |  [ 1 0 0 0 0 0 0 1 ] | [ 0 1 1 1 1 1 1 1 ]
    256 bytes       |  [ 1 0 0 0 0 0 1 0 ] | [ 0 0 0 0 0 0 0 0 ]

Let's have a look at the following example:  

    new Request()
      .putByte   (0, 0x00)    // 1 byte payload,  1 length-byte
      .putString (1, "hello") // 5 bytes payload, 1 length-byte 
      .putInteger(4, 255)     // 1 byte payload,  1 length-byte

Encoded Request:

- 1 request start byte
- 3 payloads, together 7 payload bytes
- 1 length byte / payload
- 1 index byte / payload

result: 13 serialized bytes

Pseude code:
    r = new Request()
    r.addRequestInitializer() # 0x00  
    for payload in payloadsToEncode:
        r.addPayloadLength(payload.length)
        r.addPayloadIndex(payload.index)
        r.addPayloadContent(payload.content)
  
    0x00 | 0x01 | 0x00 | 0x00 | 0x05 | 0x01 | hello | 0x01 | 0x04 | 255
    |      |      |      |      |      |      |       |      |      |
    |      |      |      |      |      |      |       |      |      +- last payload: 255 (1 byte)
    |      |      |      |      |      |      |       |      +-------- index of last payload: 4
    |      |      |      |      |      |      |       +--------------- length of last payload: 1 byte
    |      |      |      |      |      |      |
    |      |      |      |      |      |      +- second payload: "hello" (5 bytes)
    |      |      |      |      |      +-------- index of second payload: 1
    |      |      |      |      +--------------- length of second payload: 5 bytes
    |      |      |      |
    |      |      |      |       
    |      |      |      +- first payload: 0x00
    |      |      +-------- index of first payload: 0
    |      +--------------- length of first payload: 1 byte
    |   
    +- request initializer. unique. used to find start of a binary request

The index for each payload addresses the following problem: What to do if a 
payload contains 0 bytes, because a length byte with value 0x00 would be 
interpreted as the start-byte of a new request. Protocol buffers addresses
this problem by having object blueprints which are mapped to the actual 
data structures, similar to the indexes which are used here.

The index for each payload works the same way as the variable length-bytes in 
that only the lower (right) 7 bits are used, and the left bit is used to
indicate if this is the last index-byte (0) or if the next byte also counts
to the index value.
 
