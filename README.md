Overview
========

Binary Serializer provides a leightweight binary serialization protocol and 
methods for encoding and decoding. One request can contain multiple payloads
and the output is a binary request with minimal serialization overhead. The 
serialization works similar to [Protocol Buffers] [1], using a variable
amount of length-bytes indicating the number of bytes to read for the next
payload. 

Where this project differs from protobuf is that it provides only the 
binary serialization functionality, without object boilerplates used to 
decode a request into a ready-to-use object, and no support for storing arrays.
This projects accesses the payloads by integers [0..n], eg. 
``newRequest.put(index, "first payload")`` and ``decodedRequest.getString(index)``.

Furthermore this serialization protocol provides a way to separate multiple 
stacked requests via the 0x00 request start byte which acts as delimiter. 
This is useful in case of having multiple requests arrive at once when reading 
from a socket, which often happens with mobile devices when sending many requests 
in a short time.

  [1]: http://code.google.com/p/protobuf/

Example
-------

Let's have a look at the following example:  

    new Request()
      .putByte   (2, 0x00)    // 1 byte payload,  1 length-byte, 1 index-byte
      .putString (4, "hello") // 5 bytes payload, 1 length-byte, 1 index-byte
      .putInteger(7, 255)     // 1 byte payload,  1 length-byte, 1 index-byte

**Encoded Request**

    00 | 01 02 00 | 05 04 h e l l o | 01 07 255

- 1 request start byte
- 3 payloads, together 7 payload bytes
- 1 length byte / payload
- 1 index byte / payload

**Resulting package**

    0x00 | 0x01 | 0x02 | 0x00 | 0x05 | 0x04 | hello | 0x01 | 0x07 | 255
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

**Pseude code for the serialization process**

    r = new Request()
    r.addRequestInitializer() # 0x00  
    for payload in payloadsToEncode:
        r.addPayloadLength(payload.length)
        r.addPayloadIndex(payload.index)
        r.addPayloadContent(payload.content)

     
Length and Index Bytes - Base 128 Varints 
-----------------------------------------
The protocol buffers documentation explains it very well:
> To understand your simple protocol buffer encoding, you first need to understand varints. Varints are a method of serializing integers using one or more bytes. Smaller numbers take a smaller number of bytes.
>
> Each byte in a varint, except the last byte, has the most significant bit (msb) set – this indicates that there are further bytes to come. The lower 7 bits of each byte are used to store the two's complement representation of the number in groups of 7 bits, least significant group first.
>
> http://code.google.com/apis/protocolbuffers/docs/encoding.html#varints

Length and index bytes are base-128 varints prepending every payload. They represent 
the payload's size in bytes and the index used to access it. 

    Bit Values: [ x | 64 | 32 | 16 | 8 | 4 | 2 | 1 ]
                  | 
                  + last-varint-byte indicator (0=last, 1=next-also-length-byte)
  
Since each varint-byte uses only 7 bits for representing the number, the following
limits arise:
  
    One varint-byte:  7 bits   = 2^7  = 0..127
    Two varint-bytes: 2*7 bits = 2^14 = 0..16383  

A number greater than 16383 would generate a third varint-byte.

    number  |  [  varint byte 1  ] | [  varint byte 0  ]  
    --------+----------------------+---------------------  
        1   |                      | [ 0 0 0 0 0 0 0 1 ]
      127   |                      | [ 0 1 1 1 1 1 1 1 ]
      128   |  [ 1 0 0 0 0 0 0 1 ] | [ 0 0 0 0 0 0 0 0 ]  
      255   |  [ 1 0 0 0 0 0 0 1 ] | [ 0 1 1 1 1 1 1 1 ]
      256   |  [ 1 0 0 0 0 0 1 0 ] | [ 0 0 0 0 0 0 0 0 ]
    16383   |  [ 1 1 1 1 1 1 1 1 ] | [ 0 1 1 1 1 1 1 1 ]
