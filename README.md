# Python Password Utility

**Cryptographically secure, easy-to-use, password generator**

Most password generators written in Python make use of Python's
secrets module to generate random values.
**Python Password Utility** goes a step further: it chains together
a keyed version of the SHA-512 (or SHA3-512) hash function
to create a password which is computationally infeasible to guess, even for someone
who knows the internal state of the secrets module.

**Python Password Utility** can be run directly from the command line,
or called through a Python API.

This software has only been tested on Python 3.
It will refuse to run on other versions of Python.

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

## From the Command Line

```
python -m passutil <character sets> <password length> <random keyboard smashing, optional>
```

### Character sets

Character sets include:
- `c` or `u` -> A-Z
- `l` -> a-z
- `n` -> 0-9
- `p` -> ASCII punctuation: `~!@#$%^&*()-_=+[]{}\|;:'",<.>/?
- `r` -> subset of `p`, some platforms prohibit which punctuation
characters may be used in a password, `r` omits those characters
which are most likely to be banned, leaving: !@#$%&*()-_+[]{};:,.?
- `s` -> the space character

When passed as a command line parameter, the character sets
are concatenated in any order. Example:

`nsl` will generate a password with numbers, spaces, and lowercase letters.

Character set shorthands:
- `a` -> `clnps`, all the characters
- `ar` -> `clnrs`, all the characters, except those which might be banned on some platforms
- `z` -> `clnp`, all the characters, except spaces
- `zr` -> `clnr`, all the characters, except spaces, and those which might be banned on some platforms

Individual characters my be included with `i` or excluded with `e`. Example:

`nci;de74M` will include numerals, capital letters, `;`, and `d`. It will exclude `7`, `4`, and `M`.

To include/exclude lowercase `i` or `e`, prefix them with `..`. Example:

`le..in` will include lowercase letters, but will exclude lowercase `i` and `n`.

`pi..i..e` will include punctuation, `i`, and `e`.

Some characters may need to be enclosed in parenthesis or prefixed with an escape backslash.
See: [https://www.w3schools.com/python/gloss_python_escape_characters.asp](https://www.w3schools.com/python/gloss_python_escape_characters.asp)

### Password length

The password length can be any nonnegative integer.

### Random keyboard smashing

Hitting a bunch of random keys after the password length is encouraged!

The entire command will be used to generate a key for the hash function.
The more gibberish there is, the harder it will be for an
adversary to retroactively gain information about the
internal state of the password generator.

### Examples

```
python -m passutil uln 10 jti43gnnig4rng
X4TKHzTtWD
```

```
python -m passutil zr 15
{T7:b[mZ}JEs0+A
```

```
python -m passutil a 20 skyscrapers are not potato
ZW$OO%si`8ZvjPk'4.vX
```

```
python -m passutil n 4
8929
```

```
python -m passutil cps 9
>,T^ )|"A
```

```
python -m passutil niabcd..ef 20 jito firoj43rfneiffk3k
58480ddb2dc6a37be278
```

### Hashing Algorithms

This module implements a cryptographic pseudo-random
number generator based on
the SHA family of hashing algorithms.

This module is currently configured to use either
SHA-2 512 or SHA-3 512, with a preference for the latter.

To determine which algorithm is being used:
```
python -m passutil -hash
```

## Importing as a Package

Python Password Utility can be imported as a package.
It provides two publicly accessible objects.
`SHA512_number` and `generate_password`.

`SHA512_number` is a numerical constant.
A value of `2` indicates that SHA-2 512 will be used for hashing.
A value of `3` indicates that SHA-3 512 will be used for hashing.

```python
import passutil

algorithm_version = passutil.SHA512_number
```

`generate_password` is a function.

```python
import passutil

password = passutil.generate_password(length, key, valid_chars)
```

`length` is a nonnegative integer representing the number of characters in the generated password.

`key` is of type `bytes`. Its length cannot be zero. This value will be incorporated
throughout the password generation process.

`valid_chars` indicates which characters may appear in the output. It may be string of the same
format as the character sets input of the command line mode. Or it may be a set of integers,
where the integers correspond to the ASCII values of the permitted characters.

The function will output a UTF-8 encoded string.