# Python Password Utility

Generates cryptographically random passwords of any desired length.
Uses the time, Python's secrets module, and random keyboard smashing
to produce passwords which are:

1. Hard to guess even if you know the time when the password was created
and the internal state of Python's secrets module (very unlikely that an
adversary would know either of these to sufficient precision anyway)
2. Patternless. Knowing part of a password gives an adversary zero
information about the rest of the password.

This software has only been tested on Python version 3,
it will refuse to load on other versions of Python.

## Usage

```
python3 pu.py <character sets> <password length> <random keyboard smashing, optional>
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

Shorthands cannot be used in conjunction with individual sets.

### Password length

The password length can be any nonnegative integer.

### Random keyboard smashing

Hitting a bunch of random keys after the password length is encouraged!

The entire command will be used to generate a random seed.
The more gibberish there is, the harder it will be for an
adversary to retroactively gain information about the
internal state of the password generator.

## Examples

```
python3 pu.py uln 10 jti43gnnig4rng
X4TKHzTtWD
```

```
python3 pu.py zr 15
{T7:b[mZ}JEs0+A
```

```
python3 pu.py a 20 skyscrapers are not potato
ZW$OO%si`8ZvjPk'4.vX
```

```
python3 pu.py n 4
8929
```

```
python3 pu.py cps 9
>,T^ )|"A
```

## Hashing Algorithms

This module implements a cryptographic pseudo-random
number generator based on
the SHA family of hashing algorithms.

This module is currently configured to use either
SHA-2 512 or SHA-3 512, with a preference for the latter.

To determine which algorithm is being used:
```
python3 pu.py -hash
```