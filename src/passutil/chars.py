character_ranges = {
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

character_ranges["u"] = character_ranges["c"]

def resolve_charstring(s):
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
        if s[i] in character_ranges:
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
            i += character_ranges[c]
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