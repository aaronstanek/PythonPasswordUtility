# Copyright Aaron Stanek 2021
# See LICENSE for more details

import sys
from .pu import SHA512_number, generate_password
from .chars import charset_size

def load_command_line_parameters():
    if len(sys.argv) < 2:
        # user did not give any input
        # display a welcome message
        raise Exception("Python Password Utility\nCryptographically secure, easy-to-use, password generator\nFull documentation at: https://github.com/aaronstanek/PythonPasswordUtility")
    elif sys.argv[1] == "--hash":
        # user entered --hash
        # tell them which version of SHA512 we are using
        raise Exception("Using SHA-"+str(SHA512_number)+" 512")
    elif sys.argv[1] == "--size":
        # user entered --size
        # check if there is another parameter after --size
        if len(sys.argv) < 3:
            raise Exception("expected valid_chars parameter after --size")
        # treat it like a charstring
        # then give the size of the resulting charset
        raise Exception(str(charset_size(sys.argv[2])))
    elif len(sys.argv) < 3:
        raise ValueError("not enough command line parameters")
    # there is at least charset and length
    valid_chars = sys.argv[1]
    try:
        # we expect the length to be a valid integer
        length = int(sys.argv[2])
    except:
        raise TypeError("length parameter should be an integer")
    key = str(sys.argv)
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
