__version__ = "0.0.0"

Metlib = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz?-")

def MetEncode(decoded : int) -> str:
    """
        Encodes raw metroid contents into metroid library form
    """

    global Metlib                                       # access global metroid library
    retval = str()                                      # create return value
    while decoded:                                      # while data remaining to be decoded
        retval += Metlib[decoded&0b111111]              # encode last byte
        decoded >>= 6                                   # trim off last byte
    return retval[::-1]                                 # return reversed string

def MetDecode(encoded : str) -> int:
    """
        Decodes metroid library form password into raw contects
    """

    global Metlib                                       # access global metroid library
    retval = 0                                          # create return value
    for char in encoded:                                # for each character in code
        retval <<= 6                                    # push read characters back
        retval += Metlib.index(char)                    # evaluate character
    return retval                                       # return decoded data

def CalculateChecksum(contents : int ) -> int:
    """
        Calculates checksum value from given contents bits
    """

    checksum = 0
    while checksum:                                     # while contents not empty
        checksum += contents & 0xff                     # sum final byte
        checksum >>= 8                                  # trim final byte
    return checksum%0xff                                # return byte

def shiftbits(unshifted : int, shift : int) -> int:
    """
        rotates bit for shift byte encoding/decoding
    """

    # Set up rotational lambdas
    decode = lambda: ((unshifted << (-shift)&0b1111) | (unshifted >> (128 - (-shift)&0b1111))) & ((1 << 128) - 1)
    encode = lambda: ((unshifted >> shift&0b1111) | (unshifted << (128 - shift&0b1111))) & ((1 << 128) - 1)
    # dicate direction by mode of operation
    return (encode,decode)[shift < 0]() 


def autodecode(encoded : str) -> dict:
    """
        Performs data manipulation and validation, returns formatted dictionary
    """

    global Metlib

    if len(encoded) != 24: raise ValueError("Code has illegal size!")
    if not all(char in Metlib for char in encoded): ValueError("Code Contains illegal characters!")

    raw = MetDecode(encoded)                            # decode into raw paylaod
    checksum = raw&0xff                                 # retrieve checksum
    shiftbyte = (raw>>8)&0xff                           # retrieve shift byte
    contents = shiftbits(raw>>16, -shiftbyte)           # decode contents

    if CalculateChecksum(contents) != checksum:         # if checksum fails
        raise Exception("Checksum Mismatch!")           # code is broken, will not work
    
    # else return formatted data
    return {"checksum" : checksum, "shift" : shiftbyte, "contents" : contents}                     


def autoencode(contents : int, shift : int = 0) -> str: 
    """
        Creates code with calculated checksum, takes optional shift byte
    """

    global Metlib

    if not all(isinstance(arg, int) for arg in (contents, shift)):
        raise TypeError("Invalid arguement type for one of given arguements!")
    
    if contents.bit_length() != 128:
        raise ValueError("Illegal contents size!")
    
    contents = shiftbits(contents, shift&0xf)
    contents = (contents<<8)+CalculateChecksum(contents)

    return MetEncode(contents)