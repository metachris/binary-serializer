*Prototypes only -- please do not yet expect a fully working project. A protocol
finalization has yet to be made. Feedback is greatly appreciated.*

----------

This project is a **leightweight binary serialization protocol** and provides
implementations for efficient decoding and encoding multiple payloads pairs into a single 
byte stream (package). The main goals are flexibility, high encoding and decoding performance
and minimal byte and implementation overhead.

**Features**

* Minimal overhead: payloads up to 128 bytes require only one extra byte, 
  payloads up to 16384 bytes two extra bytes, ...

* Multiple concatenated packages can be separated (by using a 0x00 package start byte) 
  
* Each package contains an integer value developers can freely use to identify the 
  package type. This adds one extra byte overhead for values < 128.
     
* Support for the following data types: int, float, string, unicode, byte array

* All payloads are represented as byte arrays, there is no data type information
  inside the package. Data type information can be specified in blueprints.

* Package blueprints represent the type of content of a specific package type. They
  can be used to decode and extract a package into a dictionary

**Big-endian** ordering is used throughout the protocol for all bits in a byte, and 
all bytes in byte-groups (i.e. the most significant comes first, followed by less significant).

The serialization works similar to [Protocol Buffers] [1], using a variable
amount of length-bytes (base-128 varints) to indicate the number of bytes to read for the next
payload.

  [1]: http://code.google.com/p/protobuf/


Example
-------

Let's build a simple example request:   

    encoder = BinaryEncoder()
    encoder.setType(13)
    encoder.put(0, "hello")
    encoder.put(1, 123)
    # payload 2 not set, 0x00 will be inserted by default
    encoder.put(3, "world")
    
    result = encoder.encode()

**Encoded Request**

    00 13 | 05 h e l l o | 01 123 | 01 00 | 05 w o r l d

- 1 package start byte (0x00)
- 1 package type byte (0x13)
- 4 payloads, together 12 payload bytes
- 1 index byte / payload

**Resulting package**

    0x00   0x13   0x05   hello  0x01   123    0x10    0x00   0x05   world
    |      |      |      |      |      |      |       |      |      |
    |      |      |      |      |      |      |       |      |      +- last payload: "world"
    |      |      |      |      |      |      |       |      +-------- length of last payload: 5
    |      |      |      |      |      |      |       |
    |      |      |      |      |      |      |       +- third payload: 0x00
    |      |      |      |      |      |      +--------- length of third payload: 1 byte
    |      |      |      |      |      |      
    |      |      |      |      |      +- second payload: 123
    |      |      |      |      +-------- length of second payload: 1 byte
    |      |      |      |       
    |      |      |      +- first payload: "hello"
    |      |      +-------- length of first payload: 5 bytes
    |      |    
    |      +- package type
    +-------- package start byte

**Pseude code for the serialization process**

    result = bytearray()
    result.insert(0, 0x00) # request start byte  
    result.insert(packageType)
    
    for payload in payloadsToEncode:
        result.extend(payload.length_varint_bytes)
        result.extend(payload.content_bytes)


Length Bytes 
------------  
Length bytes are base-128 varints prepending every payload, representing 
the payload's size in bytes. 

     
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


