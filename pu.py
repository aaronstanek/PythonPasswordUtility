import sys

if sys.version_info.major != 3:
    raise Exception("Python Password Utility has only been tested on Python version 3. Behavior on over versions is not guaranteed.")

import hashlib
import secrets
import time

def SHA512(bytes_in):
    # bytes_in is a bytes object
    # returns a bytes object which is
    # the hash of bytes_in
    return SHA512.func(bytes_in).digest()

# try to use SHA-3 if possible

try:
    SHA512.func = hashlib.sha3_512
    # if SHA-3 is not supported
    # then the line above will throw
    # an exception
    SHA512.number = 3
except:
    SHA512.func = hashlib.sha512
    SHA512.number = 2

class UniqueCounter(object):
    def __init__(self):
        self.n = 0
        for i in range(16):
            self.n = (self.n*256) + secrets.randbelow(256)
    def __call__(self):
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

def generate_password(length,random_seed,valid_chars):
    if type(length) != int:
        raise TypeError("length must be int")
    if length < 0:
        raise ValueError("length must be nonnegative")
    if type(random_seed) != bytes:
        raise TypeError("random_seed must be bytes")
    if len(random_seed) < 1:
        raise ValueError("random_seed has minimum length 1")
    if type(valid_chars) != set:
        if type(valid_chars) != str:
            raise TypeError("valid_chars must be set or str")
        valid_chars = generate_password_resolve_charstring(valid_chars)
    if len(valid_chars) < 1:
        raise ValueError("valid_chars has minimum size 1")
    # length is a nonzero integer
    # random_seed is a bytes object
    # valid_chars is a set(int)
    # it indicates which characters are allowed to be in the
    # password, uses ascii codes
    # SHA512 has an output size of 64 bytes
    garbage = SHA512( b'initialize:' + random_seed )
    counter = UniqueCounter()
    for i in range(3):
        garbage = SHA512( b'prefix:' + counter() + garbage + time_hash() + secrets.token_bytes(64) + random_seed )
    # garbage is a bytes object
    # predicting its value at this point in the program should be
    # nearly impossible
    password = [] # store it as a list of ascci values, convert to a string later
    while len(password) < length:
        # update garbage
        garbage = SHA512( b'step:' + counter() + garbage + time_hash() + secrets.token_bytes(64) + random_seed )
        # use garbage to generate another sequence of byte which will not
        # have any effect on future values of garbage
        candidate = SHA512( b'output:' + counter() + garbage + time_hash() + secrets.token_bytes(64) )
        # select a single value from that string of bytes
        value = candidate[secrets.randbelow(len(candidate))]
        # predicting value is very very difficult
        # determining garbage from value requires inverting
        # a SHA512 hash (a hash which isn't even known to
        # a potential adversary because it never leaves this function)
        # determing a value from the values before and after it
        # requires at least partical knowledge of garbage
        # now convert value to a usable character
        while True:
            value ^= secrets.randbelow(256)
            if value in valid_chars:
                break
        # value is now a valid character
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
            se += s[i:]
            break
        if s[i] in generate_password_character_ranges:
            se += s[i]
        elif s[i] == "a":
            if i == len(s) - 1:
                se += "clnps"
            elif s[i+1] == "r":
                se += "clnrs"
            else:
                se += "clnps"
        elif s[i] == "z":
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
    for c in se:
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

def load_command_line_parameters():
    if len(sys.argv) > 1:
        if (sys.argv[1] == "-hash"):
            print("Using SHA-"+str(SHA512.number)+" 512")
            exit(0)
    if len(sys.argv) < 3:
        raise ValueError("not enough command line parameters")
    valid_chars = sys.argv[1]
    try:
        length = int(sys.argv[2])
    except:
        raise TypeError("second command line argument should be an integer")
    random_seed = str(sys.argv).encode("UTF-8")
    return valid_chars, length, random_seed

def main():
    valid_chars, length, random_seed = load_command_line_parameters()
    password = generate_password(length, random_seed, valid_chars)
    print(password)

if __name__ == "__main__":
    main()
