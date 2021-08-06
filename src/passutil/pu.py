import sys

if sys.version_info.major != 3:
    raise Exception("Python Password Utility has only been tested on Python version 3. Behavior on over versions is not guaranteed.")

import hashlib
import secrets
import time

# try to use SHA-3 if possible

if "sha3_512" in hashlib.algorithms_available:
    SHA512 = lambda x : hashlib.sha3_512(x).digest()
    SHA512_number = 3
else:
    SHA512 = lambda x : hashlib.sha512(x).digest()
    SHA512_number = 2

class UniqueCounter(object):
    # this class is used to guarantee
    # that the input to every hash
    # is different
    def __init__(self):
        # set the internal state to a random integer
        # 0 <= n < 2**128
        self.n = 0
        for i in range(16):
            self.n = (self.n*256) + secrets.randbelow(256)
    def __call__(self):
        # return the internal state
        # as a decimal number,
        # in a bytes format.
        # increment the internal state.
        s = str(self.n) + ":"
        self.n += 1
        return s.encode("UTF-8")

def time_hash():
    # a hash based on the current time
    t = time.time()
    t = "{:1.20f}".format(t)
    # include 20 decimal points of the time
    # this will include sub-precision garbage
    # as no reasonable computer can measure
    # durations less than 100 yoctoseconds
    t = t.encode("UTF-8")
    t = SHA512(t)
    return t

def generate_password(length,key,valid_chars):
    if type(length) != int:
        raise TypeError("length parameter must be int")
    if length < 0:
        raise ValueError("length parameter must be nonnegative")
    if type(key) != bytes:
        raise TypeError("key parameter must be bytes")
    if len(key) < 1:
        raise ValueError("key parameter has minimum length 1")
    if type(valid_chars) != set:
        if type(valid_chars) != str:
            raise TypeError("valid_chars parameter must be set or str")
        valid_chars = generate_password_resolve_charstring(valid_chars)
    if len(valid_chars) < 1:
        raise ValueError("valid_chars parameter has minimum size 1")
    for value in valid_chars:
        if type(value) != int:
            raise ValueError("valid_chars set may only contain type int")
        if value < 32 or value > 126:
            raise ValueError("valid_chars set may only contain values 32 to 126 inclusive")
    char_map = create_character_map(valid_chars)
    # length is a nonzero integer
    # key is a bytes object
    # valid_chars is a set(int)
    # it indicates which characters are allowed to be in the
    # password, uses ascii codes
    # char_map is a list of length 256
    # it maps indicies to characters in valid_chars
    # or to None
    # SHA512 has an output size of 64 bytes
    garbage = SHA512( b'initialize:' + key )
    counter = UniqueCounter()
    for i in range(3):
        # tumble the bits around
        # but don't extract any password characters yet
        garbage = SHA512( b'prefix:' + counter() + garbage + time_hash() + secrets.token_bytes(64) + key )
    # garbage is a bytes object
    # predicting its value at this point in the program should be
    # nearly impossible
    password = [] # store it as a list of ascci values, convert to a string later
    while len(password) < length: # this is the password generation loop
        # update garbage
        garbage = SHA512( b'step:' + counter() + garbage + time_hash() + secrets.token_bytes(64) + key )
        # use garbage to generate another sequence of bytes which will not
        # have any effect on future values of garbage
        candidate = SHA512( b'output:' + counter() + garbage + time_hash() + secrets.token_bytes(64) )
        # candidate should have nothing in common with future or past values of garbage
        # select a single value from those bytes
        value = candidate[secrets.randbelow(len(candidate))]
        # predicting value is very very difficult
        # determining garbage from value requires inverting
        # a SHA512 hash (a hash which isn't even known to
        # a potential adversary because it never leaves this function)
        # determing a value from the values before and after it
        # requires at least partial knowledge of garbage
        # now convert value to a usable character
        value = char_map[value]
        # value is now a valid character
        # or None
        if value is not None:
            password.append(value)
    # convert to a string
    password = bytes(password).decode("UTF-8")
    return password

generate_password_character_ranges = {
    "c": list(range(65,91)),
    "l": list(range(97,123)),
    "n": list(range(48,58)),
    "p": list(map(ord,[
        "`","~","!","@","#",
        "$","%","^","&","*",
        "(",")","-","_","=",
        "+","[","{","]","}",
        "\\","|",";",":","\'",
        "\"",",","<",".",">",
        "/","?"
        ])),
    "r": list(map(ord,[
        "!","@","#","$","%",
        "&","*","(",")","-",
        "_","+","[","{","]",
        "}",";",":",",",".",
        "?"
        ])),
    "s": [32]
}

generate_password_character_ranges["u"] = generate_password_character_ranges["c"]

def generate_password_resolve_charstring(s):
    # if a string is passed as valid_chars to
    # generate_password, it will need to be
    # resolved to a set
    # first expand shorthands
    se = ""
    for i in range(len(s)):
        if s[i] == "i" or s[i] == "e":
            # if we hit i or e
            # then we are past the named character sets
            # and we will be dealing with individual characters
            se += s[i:]
            break
        if s[i] in generate_password_character_ranges:
            # it's one of the base character sets
            se += s[i]
        elif s[i] == "a":
            # expand a or ar
            if i == len(s) - 1:
                se += "clnps"
            elif s[i+1] == "r":
                se += "clnrs"
            else:
                se += "clnps"
        elif s[i] == "z":
            # expand z or zr
            if i == len(s) - 1:
                se += "clnp"
            elif s[i+1] == "r":
                se += "clnr"
            else:
                se += "clnp"
        elif s[i] == "r":
            if i == 0:
                raise ValueError("valid_chars string cannot start with \"r\"")
            if s[i-1] != "a" or s[i-1] != "z":
                raise ValueError("valid_chars \"r\" can only appear after \"a\" or \"z\"")
        else:
            raise ValueError("valid_chars unexpected character")
    active_array = None
    i = []
    e = []
    ignore_char = 0
    for index in range(len(se)):
        if ignore_char > 0:
            ignore_char -= 1
            continue
        c = se[index]
        if len(se) - index >= 3:
            if se[index] == "." and se[index+1] == ".":
                value = ord(se[index+2])
                # must be ASCII printable
                if (value < 32 or value > 127):
                    raise ValueError("valid_chars must be ASCII printable")
                active_array.append(value)
                ignore_char = 2
                continue
        if c == "i":
            active_array = i
        elif c == "e":
            active_array = e
        elif active_array is None:
            # we have already checked that the character is valid
            i += generate_password_character_ranges[c]
        else:
            value = ord(c)
            # must be ASCII printable
            if (value < 32 or value > 127):
                raise ValueError("valid_chars must be ASCII printable")
            active_array.append(value)
    # now create a set
    output = set(i)
    for n in e:
        output.discard(n)
    return output

def create_character_map(valid_chars):
    # valid_chars is set(int)
    # the ints have already been validated to be
    # within the ASCII printable range
    # we will return a list maping the ints
    # 0-255 to the characters in the valid_chars set
    # or to None
    number_of_chars = len(valid_chars)
    limit = 256 - (256 % number_of_chars)
    # any numbers equal to or greater than
    # limit will map to None
    # this is to ensure an equal distribution of values
    list_of_chars = list(valid_chars)
    output = [None] * 256
    for i in range(limit):
        output[i] = list_of_chars[i % number_of_chars]
    return output

def load_command_line_parameters():
    if len(sys.argv) == 2:
        if (sys.argv[1] == "help"):
            raise Exception("Full documentation at: https://github.com/aaronstanek/PythonPasswordUtility")
        if (sys.argv[1] == "hash"):
            raise Exception("Using SHA-"+str(SHA512_number)+" 512")
    if len(sys.argv) < 3:
        raise ValueError("not enough command line parameters")
    valid_chars = sys.argv[1]
    try:
        length = int(sys.argv[2])
    except:
        raise TypeError("second command line argument should be an integer")
    key = str(sys.argv).encode("UTF-8")
    return valid_chars, length, key

def main():
    try:
        valid_chars, length, key = load_command_line_parameters()
        password = generate_password(length, key, valid_chars)
        print(password)
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()
