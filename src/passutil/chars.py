character_ranges = {
    "u": list(range(65,91)),
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
    "s": [32],
    "h": list(map(ord,[
        "0","1","2","3","4",
        "5","6","7","8","9",
        "a","b","c","d","e",
        "f"
    ])),
    "H": list(map(ord,[
        "0","1","2","3","4",
        "5","6","7","8","9",
        "A","B","C","D","E",
        "F"
    ]))
}

character_ranges["c"] = character_ranges["u"]

def resolve_charstring(s):
    # if a string is passed as valid_chars to
    # generate_password, it will need to be
    # resolved to a set
    output = set()
    mode = 0
    # mode = 0 is the main part, before i or e
    # mode = 1 is after the i token
    # mode = 2 is after the e token
    index = 0
    while index < len(s):
        if mode == 0:
            # mode = 0
            # main section
            if s[index] in character_ranges:
                for codepoint in character_ranges[s[index]]:
                    output.add(codepoint)
            elif s[index] == "a":
                # we have a or ar
                if index+1 < len(s):
                    if s[index+1] == "r":
                        # we have ar
                        for codepoint in resolve_charstring("ulnrs"):
                            output.add(codepoint)
                        index += 2
                        continue
                # we have a
                for codepoint in resolve_charstring("ulnps"):
                    output.add(codepoint)
            elif s[index] == "z":
                # we have z or zr
                if index+1 < len(s):
                    if s[index+1] == "r":
                        # we have zr
                        for codepoint in resolve_charstring("ulnr"):
                            output.add(codepoint)
                        index += 2
                        continue
                # we have z
                for codepoint in resolve_charstring("ulnp"):
                    output.add(codepoint)
            elif s[index] == "i":
                mode = 1
            elif s[index] == "e":
                mode = 2
            else:
                raise ValueError("Unexpected character in valid_chars")
        else:
            # mode = 1 or 2
            # i or e section
            if index+1 < len(s):
                if s[index] == "." and s[index+1] == ".":
                    # we have an escape sequence
                    if index+2 >= len(s):
                        raise("Unexpected end-of-input in valid_chars after ..")
                    if s[index+2] == "i":
                        codepoint = 105
                    elif s[index+2] == "e":
                        # switch to mode 2
                        codepoint = 101
                    else:
                        raise Exception("Unexpected character in valid_chars after ..")
                    if mode == 1:
                        output.add(codepoint)
                    else:
                        output.discard(codepoint)
                    index += 3
                    continue
            if s[index] == "i":
                mode = 1
            elif s[index] == "e":
                mode = 2
            else:
                codepoint = ord(s[index])
                if codepoint >= 32 and codepoint <= 126:
                    if mode == 1:
                        # i mode
                        output.add(codepoint)
                    else:
                        # e mode
                        output.discard(codepoint)
                else:
                    raise Exception("valid_chars must be ASCII printable")
        index += 1
    return output

def resolve_charset(x):
    # x is a set, list, or tuple
    # containing unkown types
    # returns a set containing only int
    # scans for invalid codepoints
    output = set()
    for element in x:
        if type(element) == int:
            pass
        elif type(element) == str:
            if len(element) != 1:
                raise ValueError("valid_chars set input may not contain strings with lengths other than 1")
            element = ord(element)
        else:
            raise TypeError("valid_chars set input may only contain int and str")
        if element >= 32 and element <= 126:
            output.add(element)
        else:
            raise Exception("valid_chars must be ASCII printable")
    return output

def normalize_valid_chars(x):
    # x is any type
    # if we can convert x to a valid_chars set
    # then we will, otherwise throw an exception
    if type(x) == str:
        return resolve_charstring(x)
    elif type(x) in [set,list,tuple]:
        return resolve_charset(x)
    else:
        raise TypeError("valid_chars parameter must be str, set, list, or tuple")

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
