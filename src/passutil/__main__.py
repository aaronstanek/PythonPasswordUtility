import sys
from .pu import SHA512_number, generate_password
from .chars import normalize_valid_chars

def load_command_line_parameters():
    if len(sys.argv) == 2:
        if sys.argv[1] == "--help":
            raise Exception("Full documentation at: https://github.com/aaronstanek/PythonPasswordUtility")
        if sys.argv[1] == "--hash":
            raise Exception("Using SHA-"+str(SHA512_number)+" 512")
    elif len(sys.argv) == 3:
        if sys.argv[1] == "--size":
            valid_chars = normalize_valid_chars(sys.argv[2])
            raise Exception(str(len(valid_chars)))
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
