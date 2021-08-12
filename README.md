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

This software requires Python 3.6 or later.
Major versions of Python after Python 3 are not supported.

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
python -m passutil <character set> <password length> <random keyboard smashing, optional>
```

`<character set>` tells the program which characters are permitted in your password.
`z` is generally the best option, unless there are restrictions on which
characters may appear in the password.

`<password length>` is the desired length of the password. This can be any nonnegative integer.

`<random keyboard smashing>` is an optional parameter. The entire command is taken as the key
for the hash function, so going wild on the keyboard after the `<password length>` will
increase the randomness of the generated password.

### Character sets

#### The basic character sets include:
- `u` or `c`  -> uppercase/capital: **A-Z** (26 chars)
- `l` -> lowercase: **a-z** (26 chars)
- `n` -> numeral: **0-9** (10 chars)
- `p` -> ASCII punctuation: **\`~\!@\#$%^&\*\(\)\-\_=\+\[\]\{\}\\|;:'",<\.>/?** (32 chars)
- `r` -> subset of `p`, some systems prohibit which punctuation
characters may be used in a password, `r` omits those characters
which are most likely to be banned, leaving: **\!@\#$%&\*\(\)\-\_\+\[\]\{\};:,\.?** (21 chars)
- `s` -> the space character (1 char)

**Example:**

The command below will generate a password of length 4,
containing only the numerals **0-9**.
It does this by specifying the character set `n` for numerals,
and the length `4`.
The output might look like: `7014`.

```
python -m passutil n 4
```

**Example:**

The command below will generate a password of length 25,
containing only ASCII punctuation characters.
It does this by specifying the character set `p` for punctuation,
and the length `25`.
The output might look like: `$/:<"/\~(+#/=";-:^(*)+'?-`.

```
python -m passutil p 25
```

#### If we want to use characters from multiple of character sets, we can perform a union on the sets simply by concatenating their names in the command.

**Example:**

The command below will generate a password of length 10,
containing numerals, spaces, and lowercase letters.
It does this by combining the `n`, `s`, and `l` sets,
to get the `nsl` set.
The output might look like: `p ltaj0k3p`.

```
python -m passutil nsl 10
```

#### It is also possible to combine many character sets at once using shorthands:
- `a` = `ulnps`, all the characters (95 chars)
- `ar` = `ulnrs`, all the characters, except those which are likely to be banned (84 chars)
- `z` = `ulnp`, all the characters, except spaces (94 chars)
- `zr` = `ulnr`, all the characters, except spaces, and those which are likely to be banned (83 chars)

**Example:**

The command below will generate a password of length 16,
any ASCII printable characters. It does this by using the `a`
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
containing uppercase letters, lowercase letters, numerals,
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
containing numerals, as well as `A` characters and `b` characters.
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
containing capital letters, and ASCII punctuation.
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
See: [https://www.w3schools.com/python/gloss_python_escape_characters.asp](https://www.w3schools.com/python/gloss_python_escape_characters.asp)

#### To include/exclude lowercase `i` or `e`, escape them with a `..` prefix.

**Example:**

The command below will generate a password of length 14,
containing non-vowel characters in the English alphabet.
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
containing even numerals, `a` characters, and `m` characters.
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
containing numerals, as well as `e` characters,
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

**Python Password Utility** generates passwords using either
the SHA-2 512 algorithm or the SHA-3 512 algorithm.

To determine which algorithm is being used:
```
python -m passutil --hash
```

## Calling from Python

**Python Password Utility** provides two publicly accessible objects.
`SHA512_number` and `generate_password`.

`SHA512_number` is an `int` constant.
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

`length` is a nonnegative `int` representing the number of characters in the generated password.

`key` is of type `bytes`. Its length cannot be zero. This value will be used to key the
SHA hash function.

`valid_chars` indicates which characters may appear in the output. It may be a `str` of the same
format as the `<character set>` parameter of the command line mode. Or it may be a `set` of `int`,
where the integers correspond to the ASCII values of the permitted characters.

The function will output a `str` containing the password.