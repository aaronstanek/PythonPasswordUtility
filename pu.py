import sys
import hashlib
import secrets
import time

if sys.version_info.major != 3:
    raise Exception("Python Password Utility has only been tested on Python version 3. Behavior on over versions is not guaranteed.")

def SHA512(bytes_in):
    # bytes_in is a bytes object
    # returns a bytes object which is
    # the hash of bytes_in
    return hashlib.sha512(bytes_in).digest()

def time_hash():
    # a hash based on the current time
    t = time.time()
    t = str(t)
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
        raise TypeError("valid_chars must be set")
    if len(valid_chars) < 1:
        raise ValueError("valid_chars has minimum size 1")
    # length is a nonzero integer
    # random_seed is a bytes object
    # valid_chars is a set(int)
    # it indicates which characters are allowed to be in the
    # password, uses ascii codes
    # SHA512 has an output size of 32 bytes
    garbage = random_seed
    for i in range(2 + secrets.randbelow(3)):
        garbage = SHA512( random_seed + garbage + secrets.token_bytes(32) + time_hash() )
    # garbage is a bytes object
    # predicting its value at this point in the program should be
    # nearly impossible
    password = [] # store it as a list of ascci values, convert to a string later
    while len(password) < length:
        # update garbage
        garbage = SHA512( random_seed + garbage + time_hash() + secrets.token_bytes(32) )
        # use garbage to generate another sequence of byte which will not
        # have any effect on future values of garbage
        candidate = SHA512( secrets.token_bytes(32) + time_hash() + garbage )
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

def load_command_line_parameters():
    if len(sys.argv) < 3:
        raise ValueError("not enough command line parameters")
    char_sets = sys.argv[1]
    try:
        length = int(sys.argv[2])
    except:
        raise TypeError("second command line argument should be an integer")
    random_seed = str(sys.argv).encode("UTF-8")
    return char_sets, length, random_seed

def determine_valid_chars(char_sets):
    # translate shorthand codes
    if char_sets == "a":
        char_sets = "clnps"
    elif char_sets == "ar":
        char_sets = "clnrs"
    elif char_sets == "z":
        char_sets = "clnp"
    elif char_sets == "zr":
        char_sets = "clnr"
    # build valid_chars set
    valid_chars = set()
    for set_name in char_sets:
        if set_name == "c" or set_name == "u":
            # capital letters
            chars = list(range(65,91))
        elif set_name == "l":
            # lowercase letters
            chars = list(range(97,123))
        elif set_name == "n":
            # numbers
            chars = list(range(48,58))
        elif set_name == "p":
            # punctuation
            chars = [
                "`","~","!","@","#",
                "$","%","^","&","*",
                "(",")","-","_","=",
                "+","[","{","]","}",
                "\\","|",";",":","\'",
                "\"",",","<",".",">",
                "/","?"
                ]
            chars = list(map(ord,chars))
        elif set_name == "r":
            # restricted punctuation
            chars = [
                "!","@","#","$","%",
                "&","*","(",")","-",
                "_","+","[","{","]",
                "}",";",":",",",".",
                "?"
                ]
            chars = list(map(ord,chars))
        elif set_name == "s":
            chars = [32]
        else:
            raise ValueError("unknown character set: "+set_name)
        for x in chars:
            valid_chars.add(x)
    return valid_chars

def main():
    char_sets, length, random_seed = load_command_line_parameters()
    valid_chars = determine_valid_chars(char_sets)
    password = generate_password(length, random_seed, valid_chars)
    print(password)

if __name__ == "__main__":
    main()
