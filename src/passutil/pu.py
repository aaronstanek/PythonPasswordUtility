import sys

if sys.version_info.major != 3:
    raise Exception("Python Password Utility has only been tested on Python version 3. Behavior on over versions is not guaranteed.")

import hashlib
import secrets
import time
from .chars import normalize_valid_chars, create_character_map

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
    valid_chars = normalize_valid_chars(valid_chars)
    if len(valid_chars) < 1:
        raise ValueError("valid_chars parameter has minimum size 1")
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
