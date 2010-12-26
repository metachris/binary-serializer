*Prototypes only -- please do not yet expect a fully working project. A protocol
finalization has yet to be made. Feedback is greatly appreciated.*

-----

Binary Serializer proposes a **leightweight binary serialization protocol** and provides
methods for decoding and encoding key-value pairs into a byte stream. 

This serialization protocol uses **integer-keys** to access the values which can be of
any primitive data type (including int, float, string, byte array). **Big-endian** 
ordering is used throughout the protocol for all bits in a byte, and all bytes in 
byte-groups (i.e. the most significant comes first, followed by less significant).

The serialization works **similar to [Protocol Buffers] [1]**, using a variable
amount of length-bytes indicating the number of bytes to read for the next
payload (base-128 varints). Protocol Buffers differs in three significant ways:

  [1]: http://code.google.com/p/protobuf/

* Protobuf requires object boilerplates (.proto files) to be compiled into object prototypes 
  before being able to use it, whereas this project provides a runtime key-value dictionary 
  using integer-only keys. This approach combines the performance and efficiency of protocol 
  buffers with some of the flexibility of json, while greatly reducing the code needed to 
  implement the protocol. 
 
* This serialization protocol provides a way to separate multiple concatenated requests 
  via the 0x00 request start byte which acts as request delimiter.
  
* Protobuf stores the bytes of base-128 varints in little-endian byte-groups (least
  significant byte first), whereas this project uses big-endian everywhere including 
  for the order in varint byte-groups (most significant byte comes first in the bytestream).


Example
-------

Let's build a simple example request:   

    encoder = BinaryEncoder()
    encoder.put(2, 0x00)    // 1 byte payload,  1 length-byte, 1 index-byte
    encoder.put(4, "hello") // 5 bytes payload, 1 length-byte, 1 index-byte
    encoder.put(7, 255)     // 1 byte payload,  1 length-byte, 1 index-byte
    
    result = encoder.encode()

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
    |      |      |      |      |      |      |       |      +-------- index of last payload: 7
    |      |      |      |      |      |      |       +--------------- length of last payload: 1 byte
    |      |      |      |      |      |      |
    |      |      |      |      |      |      +- second payload: "hello" (5 bytes)
    |      |      |      |      |      +-------- index of second payload: 4
    |      |      |      |      +--------------- length of second payload: 5 bytes
    |      |      |      |
    |      |      |      |       
    |      |      |      +- first payload: 0x00
    |      |      +-------- index of first payload: 2
    |      +--------------- length of first payload: 1 byte
    |   
    +- request initializer. unique. used to find start of a binary request

**Pseude code for the serialization process**

    result = bytearray()
    result.insert(0, 0x00) # request start byte  
    
    for payload in payloadsToEncode:
        result.extend(payload.length_varint_bytes)
        result.extend(payload.index_varint_bytes)
        result.extend(payload.content_bytes)


Length and Index Bytes 
----------------------  
Length and index bytes are base-128 varints prepending every payload. They represent 
the payload's size in bytes and the index used to access it. 

     
Base 128 Varints 
----------------
Paraphrasing the [protocol buffers documentation] [1]:
> To understand the encoding, you first need to understand varints. Varints are a method of serializing integers using one or more bytes. Smaller numbers take a smaller number of bytes.
>
> Each byte in a varint, except the last byte, has the most significant bit (msb) set – this indicates that there are further bytes to come. The lower 7 bits of each byte are used to store the representation of the number in groups of 7 bits.

  [1]: http://code.google.com/apis/protocolbuffers/docs/encoding.html#varints

This project differs with the protobuf base-128 varint implementation: Protocol Buffers 
puts the least significant bytes first, followed by more significant bytes. This project 
keeps the natural byte order with the most significant bytes first, followed by the less 
significant bytes. 

**Byte Overview**

    Bit Values: [ x | 64 | 32 | 16 | 8 | 4 | 2 | 1 ]
                  | 
                  + last-varint-byte indicator (0=last, 1=next-also-length-byte)
  
**Limits**
Since each varint-byte uses only 7 bits for representing the number, the following
limits arise:
  
    One varint-byte:  7 bits   = 2^7  = 0..127
    Two varint-bytes: 2*7 bits = 2^14 = 0..16383  

A number greater than 16383 generates a third varint-byte, etc.

**Varint Examples**

    number  |  [  varint byte 1  ] | [  varint byte 0  ]  
    --------+----------------------+---------------------  
        1   |                      | [ 0 0 0 0 0 0 0 1 ]
      127   |                      | [ 0 1 1 1 1 1 1 1 ]
      128   |  [ 1 0 0 0 0 0 0 1 ] | [ 0 0 0 0 0 0 0 0 ]  
      255   |  [ 1 0 0 0 0 0 0 1 ] | [ 0 1 1 1 1 1 1 1 ]
      256   |  [ 1 0 0 0 0 0 1 0 ] | [ 0 0 0 0 0 0 0 0 ]
    16383   |  [ 1 1 1 1 1 1 1 1 ] | [ 0 1 1 1 1 1 1 1 ]


