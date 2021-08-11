# Copyright Aaron Stanek 2021
# See LICENSE for more details

# character_ranges maps character set names
# to their definitions
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

# c is a synonym of u
character_ranges["c"] = character_ranges["u"]

def resolve_charstring(s):
    # if a string is passed as valid_chars to
    # generate_password, it will need to be
    # resolved to a set
    # we will iterate over s
    # following the syntax rules for the this kind of charstring
    # there may optionally be a header section, with named sets
    # see character_ranges for dict of these
    # after, there may be optional sections i and e
    # i to include characters, e to exclude them
    # to include/exclude the characters i or e
    # they must be prefixed with ..
    output = set()
    mode = 0
    # mode = 0 is the header section, before i or e
    # mode = 1 is after the i token
    # mode = 2 is after the e token
    index = 0
    while index < len(s):
        if mode == 0:
            # mode = 0
            # header section
            if s[index] in character_ranges:
                # this is a named charset
                # include all the values in its definition
                for codepoint in character_ranges[s[index]]:
                    output.add(codepoint)
            elif s[index] == "a":
                # we have a or ar
                # this is a shorthand
                # replace the shorthand with its definition
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
                # this is a shorthand
                # replace the shorthand with its definition
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
                # we hit an i token,
                # start an i section
                mode = 1
            elif s[index] == "e":
                # we hit an e token,
                # start an e section
                mode = 2
            else:
                # we expect a named character set, a shorthand, or i/e
                raise ValueError("unexpected character in valid_chars")
        else:
            # mode = 1 or 2
            # i or e section
            if index+1 < len(s):
                if s[index] == "." and s[index+1] == ".":
                    # we have an escape sequence
                    # ..i or ..e
                    if index+2 >= len(s):
                        raise ValueError("unexpected end-of-input in valid_chars after ..")
                    if s[index+2] == "i":
                        codepoint = 105
                    elif s[index+2] == "e":
                        codepoint = 101
                    else:
                        # expected i or e after ..
                        raise ValueError("unexpected character in valid_chars after ..")
                    if mode == 1:
                        # we are in an i section
                        # add the escaped i or e
                        output.add(codepoint)
                    else:
                        # we are in an e section
                        # discard the escaped i or e
                        output.discard(codepoint)
                    index += 3
                    continue
            # we do not have an escape sequence
            if s[index] == "i":
                # if we hit an i token,
                # then we start an i section
                mode = 1
            elif s[index] == "e":
                # if we hit an e token,
                # then we start an e section
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
                    raise ValueError("valid_chars values must correspond to ASCII printable characters")
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
                raise ValueError("valid_chars collection input may not contain strings with lengths other than 1")
            element = ord(element)
        else:
            raise TypeError("valid_chars collection input may only contain int and str")
        if element >= 32 and element <= 126:
            output.add(element)
        else:
            raise ValueError("valid_chars values must correspond to ASCII printable characters")
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
        raise TypeError("valid_chars parameter must be of type str, set, list, or tuple")

def charset_size(x):
    # normalizes charset x
    # then returns its size
    return len(normalize_valid_chars(x))

def create_character_map(valid_chars):
    # valid_chars is set(int)
    # the ints have already been validated to be
    # within the ASCII printable range
    # we will return a list maping the ints
    # 0-255 to the character codepoints in the valid_chars set
    # or to None
    repetitions = 256 // len(valid_chars)
    # repetitions is the number of times
    # that each character in valid_chars
    # will be repeated in output
    output = []
    for character in valid_chars:
        output += [character] * repetitions
    # len(output) - repetitions * len(valid_chars)
    # will be less than len(valid_chars)
    # we will fill in the remainder of output
    # with None values to bring the length
    # to 256
    output += [None] * (256-len(output))
    return output
