# Python Password Utility

**Cryptographically secure, easy-to-use, password generator**

Most password generators written in Python make use of Python's
secrets module to generate random values.
**Python Password Utility** goes a step further: it chains together
a keyed version of the SHA-512 (or SHA3-512) hash function
to create a password which is computationally infeasible to guess, even for someone
who knows the internal state of the secrets module.

**Python Password Utility** can be
[run directly from the command line](#running-from-the-command-line),
or [called through a Python API](#calling-from-python).

This software requires Python 3.6 or later.
Major versions of Python after Python 3 are not supported.

### Index

1. [Description](#description)
1. [Installation](#installation)
1. [Running from the Command Line](#running-from-the-command-line)
    1. [Character Sets](#character-sets)
    1. [Advanced Examples of Character Sets](#advanced-examples)
    1. [Getting the Size of a Character Set](#getting-the-size-of-a-character-set)
    1. [Determining which Hashing Algorithm is being used](#hashing-algorithms)
1. [Calling from Python](#calling-from-python)
    1. [generate_password](#generate_password)
    1. [charset_size](#charset_size)
    1. [SHA512_number](#sha512_number)

## Description

The algorithm operates in a loop; at each iteration of the loop one character
is added to the password. The program takes the "output state" of the previous iteration,
and hashes it alongside the current time, 64 random bytes from Python's secrets module,
a unique counter value, and the key. The result of this operation is the "output state"
that will be used by the next iteration of the loop.

Each of the "output states" is then hashed again along with the time, a different 64 random bytes,
and a different unique counter value. One byte is selected randomly
from each of the resulting "candidate states"
and is transformed into a password character.

The power of this technique comes from the keyed hash functions. For an attacker to have any hope
of guessing a password generated in this way, they must first know the key which was used.
If the user creates a new somewhat-random key for each password, and then removes all record of the key,
it eliminates any chance of retroactively recovering the password.
This holds true even in the absurdly unlikely case that an attacker knows both the time when the
password was generated and the internal state of Python's secrets module.

Drawing randomness from multiple sources, and passing it through a SHA hash,
guarantees that the resulting passwords will be patternless: knowing any part
of the password will not give an attacker any information about the rest of the password.
Passwords generated from **Python Password Utility** will have the maximum possible
entropy for a password of their length and character set.

## Installation

```
pip install passutil
```

Note:
This software requires Python 3.6 or later.
Major versions of Python after Python 3 are not supported.

## Running from the Command Line

```
python -m passutil <valid_chars> <length> <random keyboard smashing, optional>
```

`<valid_chars>` tells the program which characters are permitted in your password.
The format of this parameter is described below.
`z` is generally the best option, unless there are restrictions on which
characters may appear in the password.
This parameter may not correspond to an empty set;
to be able to generate a password, at least one character must be
allowed to exist in the password.

`<length>` is the desired length of the password. This can be any nonnegative integer.

`<random keyboard smashing>` is an optional parameter. The entire command is taken as the key
for the hash function, so going wild on the keyboard after the `<length>` will
increase the randomness of the generated password.

### Character Sets

#### The basic character sets include:
- `u` or `c`  -> uppercase/capital: **A-Z** (26 characters)
- `l` -> lowercase: **a-z** (26 characters)
- `n` -> numeral: **0-9** (10 characters)
- `p` -> ASCII punctuation: **\`~\!@\#$%^&\*\(\)\-\_=\+\[\]\{\}\\|;:'",<\.>/?** (32 characters)
- `r` -> subset of `p`, some systems prohibit which punctuation
characters may be used in a password, `r` omits those characters
which are most likely to be banned, leaving: **\!@\#$%&\*\(\)\-\_\+\[\]\{\};:,\.?** (21 characters)
- `s` -> the space character (1 character)
- `H` -> uppercase hexadecimal characters: **0123456789ABCDEF** (16 characters)
- `h` -> lowercase hexadecimal characters: **0123456789abcdef** (16 characters)

**Example:**

The command below will generate a password of length 4,
only containing the numerals **0-9**.
It does this by specifying the character set `n` for numerals,
and the length `4`.
The output might look like: `7014`.

```
python -m passutil n 4
```

**Example:**

The command below will generate a password of length 25,
only containing ASCII punctuation characters.
It does this by specifying the character set `p` for punctuation,
and the length `25`.
The output might look like: `$/:<"/\~(+#/=";-:^(*)+'?-`.

```
python -m passutil p 25
```

#### If we want to use characters from multiple character sets, we can perform a union on the sets simply by concatenating their names in the command.

**Example:**

The command below will generate a password of length 10,
only containing numerals, spaces, and lowercase letters.
It does this by combining the `n`, `s`, and `l` sets,
to get the `nsl` set.
The output might look like: `p ltaj0k3p`.

```
python -m passutil nsl 10
```

#### It is also possible to combine many character sets at once using shorthands:
- `a` = `ulnps`, all the characters (95 characters)
- `ar` = `ulnrs`, all the characters, except those which are likely to be banned (84 characters)
- `z` = `ulnp`, all the characters, except spaces (94 characters)
- `zr` = `ulnr`, all the characters, except spaces, and those which are likely to be banned (83 characters)

**Example:**

The command below will generate a password of length 16,
containing any of the ASCII printable characters. It does this by using the `a`
shorthand. The output may look like: `~VJ &FhC[_K8wu:+`.

```
python -m passutil a 16
```

Note that the above command is fully equivalent to:

```
python -m passutil ulnps 16
```

**Example:**

The command below will generate a password of length 7,
only containing uppercase letters, lowercase letters, numerals,
restricted punctuation characters, and spaces.
It does this by combining the `zr` shorthand with the `s`
character set.
The output may look like: `1A #T-x`.

```
python -m passutil zrs 7
```

Note: `zrs` = `szr` = `ulnrs` = `ar`

(`zr` is expanded to its definition, and then merged with `s`)

However: `zsr` = `ulnpsr` = `a`

(`z` is expanded to its definition, the last `r` is ignored because it is already included in `p`)

#### Individual characters may be included with `i` or excluded with `e`.

**Example:**

The command below will generate a password of length 20,
only containing numerals, `A` characters and `b` characters.
It does this by first declaring the base set: `n`,
indicating numerals, then modifying it
with `i`. The `Ab` after the `i` signals that `A` characters
and `b` characters are allowed in the password.
The output may look like: `24b749b71A1669586098`.

```
python -m passutil niAb 20
```

**Example:**

The command below will generate a password of length 18,
only containing capital letters and ASCII punctuation.
However, it will not contain the characters `C`,
`A`, `T`, `.`, or `/`.
It does this by first declaring the base set: `cp`,
indicating capitals and punctuation, then modifying it
with `e`. The `CAT./` after the `e` signals that these
characters may not appear in the password.
The output may look like: `[W*[*;{(UM@QL,_$XR`.

```
python -m passutil cpeCAT./ 18
```

Some characters may need to be enclosed in parenthesis or prefixed with an escape backslash.
See: [https://www.shellscript.sh/escape.html](https://www.shellscript.sh/escape.html)

#### To include/exclude lowercase `i` or `e`, escape them with a `..` prefix.

**Example:**

The command below will generate a password of length 14,
only containing consonants in the English alphabet.
It does this by first declaring the base set: `l`,
indicating lowercase letters, then modifying it
with `e` to exclude the vowel characters.
Notice that in the exclusion, `e` and `i`
are prefixed with `..` to prevent them
from being interpreted as the beginning
of an exclusion or inclusion.
The output may look like: `hgydslgfzpsqft`.

```
python -m passutil lea..e..iou 14
```

#### `i` and `e` may be used together

**Example:**

The command below will generate a password of length 26,
only containing even numerals, `a` characters, and `m` characters.
It does this by first declaring the base set: `n`,
indicating numerals, then modifying it
with `i` to include `a` and `m` characters.
The following `e` will then exclude
the `1`, `3`, `5`, `7`, and `9` characters from
the password.
The output may look like: `m6am6a264m6m4m884m40aa6ma2`.

```
python -m passutil niame13579 26
```

**Example:**

The command below will generate a password of length 7,
only containing numerals, `e` characters,
and excluding the numeral `5`.
It does this by first declaring the base set: `n`,
indicating numerals, then modifying it with `i`
to include `e`. Note that the first `e` is escaped with a `..`,
and is therefore included by the preceding `i`, while the second `e`
is not escaped, and so signals the start of an exclusion.
`5` is excluded by the second `e`.
The output may look like: `97739e8`.

```
python -m passutil ni..ee5 7
```

### Advanced Examples

**Example:**

```
IN:  python -m passutil li234 30
OUT: ppkksclllnihfghmrmxqklvcleiroe
```

Where's the `234` in the output?

The `<valid_chars>` parameter controls which
characters may appear in the password,
not which characters will appear in the password.

**Example:**

```
IN:  python -m passutil aen 30
OUT: x&deJD.PHG\]-5]0d\&!CX\wRwHyNl
```

I wanted to generate a password using
all the characters, except for numerals.
What's that `5` doing in there?

After an `i` or `e` starts an inclusion or exclusion,
all subsequent characters (except for `i` and `e`)
are interpreted literally.

Before any inclusions or exclusions, `u`, `c`,
`l`, `n`, `p`, `r`, `s`, `H`, and `h` refer to sets of characters.
(Definitions given above)

Within inclusions and exclusions, these same characters
are interpreted as individual Latin alphabet
letters to be included or excluded.

So, `aen` will generate a password using all available characters
except for the lowercase letter `n`, which will be excluded.
To generate a password using all the available characters
except numerals, use `ulps` or more inconveniently `ae0123456789`.

**Example:**

```
IN:  python -m passutil iATCG 12
OUT: CACCCCCGTCTG
```

Declaring a base set is not required.
The `<valid_chars>` parameter may begin with an `i`,
followed by the characters to include.

**Example:**

```
IN:  python -m passutil ipeck 10
OUT: pppppppppp
```

What's going on here?
I wanted a password using the letters `p`,
`e`, `c`, and `k`, but I only get a bunch of `p` characters.

Because the `e` is not escaped, it is treated as the beginning
of an exclusion. `c` and `k` are excluded, leaving only `p`
in the character set.

To create a character set with the characters
`p`, `e`, `c`, and `k`, the `e` needs to be
escaped: `ip..eck`.

**Example:**

```
IN:  python -m passutil lebig 10
OUT: wdaozsgput
```

Why is there a `g` in the output? I wanted to exclude
the characters `b`, `i`, and `g`.

Same thing as the previous example.
`i` is not escaped.
The correct character set will be produced with: `leb..ig`.

**Example:**

```
IN:  python -m passutil i..i 10
OUT: iiiiiiiiii
```

Wait, what?

The first `i` starts an inclusion.
The escaped second `i` is the sole character
that is included into the set.

**Example:**

```
IN:  python -m passutil e..e 10
OUT: valid_chars parameter has minimum size 1
```

Wait, what?

The first `e` starts an exclusion.
No characters are added into the character set.
The program needs at least one valid character
to be able to produce a password.

**Example:**

```
IN:  python -m passutil ixiyey 10
OUT: xxxxxxxxxx

IN:  python -m passutil ixeyiy 10
OUT: xyyyxyyyxy
```

What's going on here?
Why do such similar inputs produce such different outputs?

The generation of the character set operates from left to right.

In the first case: `ix` will add `x` to the set.
`iy` will add `y` to the set.
But then, `ey` will remove `y` from the set,
leaving only `x`.

In the second case: `ix` will add `x` to the set.
`ey` will try to remove `y` from the set, but as
there is no `y` in the set, it will do nothing.
Then, the program reaches `iy`, adding `y` to the set,
resulting in a set containing both `x` and `y`.

### Getting the Size of a Character Set

Sometimes it is useful to know how many characters
are in a character set before the character set
is used. **Python Password Utility** allows
one to do this from the command line.

```
python -m passutil --size <valid_chars>
```

`<valid_chars>` has the same format as above.
However, unlike when generating a password,
`valid_chars` may correspond to an empty set.
In such a case, `0` is returned.

**Example:**

```
IN:  python -m passutil --size une5
OUT: 35
```

`u` has 26 characters. `n` has 10.
`e5` removes one character, leaving 35.

### Hashing Algorithms

**Python Password Utility** generates passwords using either
the SHA-2 512 algorithm or the SHA-3 512 algorithm.

To determine which algorithm is being used:
```
python -m passutil --hash
```

## Calling from Python

**Python Password Utility** provides three publicly accessible objects.
- [generate_password](#generate_password)
- [charset_size](#charset_size)
- [SHA512_number](#sha512_number)

### generate_password

`generate_password` is a function. As the name suggests,
it generates passwords in the same way that the
command line interface does.

```python
import passutil

password = passutil.generate_password(length, key, valid_chars)
```

`length` is a nonnegative `int` representing the desired number of characters in the password.

`key` is of type `bytes` or `str`. Its length cannot be zero. This value will be used to key the
SHA hash function.
For best results, use a different `key` value on each call to `generate_password`.

`valid_chars` indicates which characters may appear in the output password. It may be a `str` of the same
format as the `<valid_chars>` parameter in the command line interface.
Alternatively, `valid_chars` may be a `set`, `list`, or `tuple` containing permitted
characters, encoded as single-character strings.
Alternatively, `valid_chars` may be a `set`, `list`, or `tuple` containing
codepoints for permitted characters. Only ASCII printable characters,
or their codepoints, may given in `valid_chars`. `valid_chars` may not correspond to
an empty set.

The function will output a `str` containing the password.

Raises `TypeError` if `length` is not an `int`.
Or if `key` is not a `bytes` or `str` object.
Or if `valid_chars` is not a `str`, `set`,
`list`, or `tuple`. Or if the contained elements are neither
`str` or `int`.

Raises `ValueError` if `length` is negative.
Or if `key` has length zero.
Or if the format is incorrect.
Or if non-ASCII-printable
characters are given in `valid_chars`.

**Example:**

```python
import passutil
password = passutil.generate_password(4, "hello world", "n")
print(type(password)) # str
print(password) # 7014
```

This is analogous to the very first example given in this document.

**Example:**

```python
import passutil
password = passutil.generate_password(12, b'\xf0\x9f\x98\x84', {"A","T",67,71})
# ASCII value 67 is "C", ASCII value 71 is "G"
print(password) # CACCCCCGTCTG
```
This is analogous to one of the advanced examples above.

### charset_size

`charset_size` is the analog of `--size` in the command line interface.
It is a function called in the following way:

```python
import passutil

size = passutil.charset_size(valid_chars)
```
It returns an `int`. 
`valid_chars` has the same format as in `generate_password`.
Unlike in `generate_password`, an input corresponding to an
empty character set will not cause an exception; instead the function
will simply return `0`, indicating a character set of size zero.

Raises `TypeError` if `valid_chars` is not a `str`, `set`,
`list`, or `tuple`. Or if the contained elements are neither
`str` or `int`.

Raises `ValueError` if the format is incorrect or if non-ASCII-printable
characters are given in `valid_chars`.

### SHA512_number

`SHA512_number` is the analog of `--hash` in the command line interface. 
It is an `int` constant.
A value of `2` indicates that SHA-2 512 will be used for hashing.
A value of `3` indicates that SHA-3 512 will be used for hashing.

```python
import passutil

algorithm_version = passutil.SHA512_number
```