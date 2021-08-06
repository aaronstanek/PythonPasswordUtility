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
    "s": [32]
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
                if codepoint >= 32 and codepoint <= 127:
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