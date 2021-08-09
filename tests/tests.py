import unittest
import sys
sys.path.append("../src")
import passutil
import passutil.chars as chars

class Test_character_ranges(unittest.TestCase):
    def test_types(self):
        self.assertEqual(type(chars.character_ranges),dict)
        for key in chars.character_ranges:
            self.assertEqual(type(key),str)
            value = chars.character_ranges[key]
            self.assertEqual(type(value),list)
            for subvalue in value:
                self.assertEqual(type(subvalue),int)
                self.assertTrue(
                    subvalue >= 32 and subvalue <= 126
                )
    def test_sizes(self):
        self.assertEqual(len(chars.character_ranges["u"]),26)
        self.assertEqual(len(chars.character_ranges["c"]),26)
        self.assertEqual(len(chars.character_ranges["l"]),26)
        self.assertEqual(len(chars.character_ranges["n"]),10)
        self.assertEqual(len(chars.character_ranges["p"]),32)
        self.assertEqual(len(chars.character_ranges["r"]),21)
        self.assertEqual(len(chars.character_ranges["s"]),1)
        self.assertEqual(len(chars.character_ranges["h"]),16)
        self.assertEqual(len(chars.character_ranges["H"]),16)

class Test_resolve_charstring(unittest.TestCase):
    def test_none(self):
        result = chars.resolve_charstring("")
        self.assertEqual(type(result),set)
        self.assertEqual(len(result),0)
    def test_n(self):
        result = chars.resolve_charstring("n")
        self.assertEqual(type(result),set)
        target = set(range(48,58))
        self.assertEqual(result,target)
    def test_cn(self):
        result = chars.resolve_charstring("cn")
        self.assertEqual(type(result),set)
        target = set( list(range(65,91)) + list(range(48,58)) )
        self.assertEqual(result,target)
    def test_a(self):
        result = chars.resolve_charstring("a")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        self.assertEqual(result,target)
    def test_ar(self):
        result = chars.resolve_charstring("ar")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        for codepoint in chars.character_ranges["p"]:
            if codepoint not in chars.character_ranges["r"]:
                target.remove(codepoint)
        self.assertEqual(result,target)
    def test_z(self):
        result = chars.resolve_charstring("z")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        target.remove(32)
        self.assertEqual(result,target)
    def test_zr(self):
        result = chars.resolve_charstring("zr")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        target.remove(32)
        for codepoint in chars.character_ranges["p"]:
            if codepoint not in chars.character_ranges["r"]:
                target.remove(codepoint)
        self.assertEqual(result,target)
    def test_Hi(self):
        result = chars.resolve_charstring("Hig$")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        target = set(chars.character_ranges["H"])
        target.add(ord("g"))
        target.add(ord("$"))
        self.assertEqual(result,target)
    def test_ne(self):
        result = chars.resolve_charstring("ne85")
        self.assertEqual(type(result),set)
        target = set(chars.character_ranges["n"])
        target.discard(ord("8"))
        target.discard(ord("5"))
        self.assertEqual(result,target)
    def test_complex1(self):
        result = chars.resolve_charstring("zre1234567890i$52e..i5")
        self.assertEqual(type(result),set)
        target = set(range(32,127))
        # a
        target.remove(32)
        # z
        for codepoint in chars.character_ranges["p"]:
            if codepoint not in chars.character_ranges["r"]:
                target.remove(codepoint)
        # zr
        for codepoint in range(48,58):
            target.discard(codepoint)
        # zre1234567890
        target.add(ord("$"))
        target.add(ord("5"))
        target.add(ord("2"))
        # zre1234567890i$52
        target.discard(ord("i"))
        target.discard(ord("5"))
        # zre1234567890i$52e..i5
        self.assertEqual(result,target)
    def test_complex2(self):
        result = chars.resolve_charstring("nui$#..e..ieFe")
        target = set(range(48,58))
        for codepoint in range(65,91):
            target.add(codepoint)
        # nu
        target.add(ord("$"))
        target.add(ord("#"))
        target.add(ord("e"))
        target.add(ord("i"))
        # nui$#..e..i
        target.discard(ord("F"))
        # nui$#..e..ieF
        self.assertEqual(result,target)
    def test_safe_failure(self):
        with self.assertRaises(Exception):
            chars.resolve_charstring("q")
        with self.assertRaises(Exception):
            chars.resolve_charstring("nb")
        with self.assertRaises(Exception):
            chars.resolve_charstring("ZR")
        with self.assertRaises(Exception):
            chars.resolve_charstring("ci..t")
        with self.assertRaises(Exception):
            chars.resolve_charstring("..i")
        with self.assertRaises(Exception):
            chars.resolve_charstring("le..e..I")
        with self.assertRaises(Exception):
            chars.resolve_charstring("unl..")
        with self.assertRaises(Exception):
            chars.resolve_charstring("niā")
        with self.assertRaises(Exception):
            chars.resolve_charstring("ā")

class Test_resolve_charset(unittest.TestCase):
    def test_1(self):
        a = [] # will become set
        b = [] # stays as list
        c = [] # will become tuple
        for i in range(32,127):
            a.append(i if i % 2 else chr(i))
            b.append(i if i % 3 else chr(i))
            c.append(i if i % 5 else chr(i))
        a_in = set(a)
        b_in = b
        c_in = tuple(c)
        a_out = chars.resolve_charset(a_in)
        b_out = chars.resolve_charset(b_in)
        c_out = chars.resolve_charset(c_in)
        self.assertEqual(a_out,b_out)
        self.assertEqual(b_out,c_out)
        self.assertEqual(a_out,c_out)
    def test_safe_failure(self):
        with self.assertRaises(Exception):
            chars.resolve_charset([None])
        with self.assertRaises(Exception):
            chars.resolve_charset(("hi","there"))
        with self.assertRaises(Exception):
            chars.resolve_charset({"ā"})

class Test_create_character_map(unittest.TestCase):
    def test_1(self):
        result = chars.create_character_map(chars.resolve_charstring("n"))
        is_none = 0
        counts = {}
        for elem in result:
            if elem is None:
                is_none += 1
            elif elem in counts:
                counts[elem] += 1
            else:
                counts[elem] = 1
        self.assertEqual(is_none,6)
        self.assertTrue(all(map(lambda key: counts[key] == 25, counts)))
    def test_2(self):
        result = chars.create_character_map(chars.resolve_charstring("uneE5"))
        is_none = 0
        counts = {}
        for elem in result:
            if elem is None:
                is_none += 1
            elif elem in counts:
                counts[elem] += 1
            else:
                counts[elem] = 1
        self.assertEqual(is_none,18)
        self.assertTrue(all(map(lambda key: counts[key] == 7, counts)))

class Test_generate_password(unittest.TestCase):
    def test_1(self):
        result = passutil.generate_password(0,"hi","iABC")
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),0)
    def test_2(self):
        result = passutil.generate_password(5000,b'hi',"c")
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),5000)
        found = [False] * 26
        for char in result:
            number = ord(char)
            self.assertTrue(number >= 65 and number <= 90)
            found[number - 65] = True
        self.assertTrue(all(found))
    def test_3(self):
        result = passutil.generate_password(10,"tomato",{65,97})
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),10)
        for char in result:
            number = ord(char)
            self.assertTrue(number == 65 or number == 97)
    def test_4(self):
        result = passutil.generate_password(21,b'tomato',("h","W",32,126))
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),21)
        for char in result:
            self.assertTrue(char in ["h","W"] or ord(char) in [32,126])
    def test_5(self):
        result = passutil.generate_password(1000,"password",["a","e","5","y"])
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),1000)
        for char in result:
            self.assertTrue(char in ["a","e","5","y"])
    def test_6(self):
        result = passutil.generate_password(5000,b'password',"ae5y")
        self.assertEqual(type(result),str)
        self.assertEqual(len(result),5000)
        counts = {}
        for char in result:
            self.assertFalse(char == "5" or char == "y")
            if char in counts:
                counts[char] += 1
            else:
                counts[char] = 1
        self.assertEqual(len(counts),93)
    def test_safe_failure(self):
        with self.assertRaises(Exception):
            passutil.generate_password("0","hi","iABC")
        with self.assertRaises(Exception):
            passutil.generate_password(-10,"hi","iABC")
        with self.assertRaises(Exception):
            passutil.generate_password(0,"","iABC")
        with self.assertRaises(Exception):
            passutil.generate_password(0,b'',"iABC")
        with self.assertRaises(Exception):
            passutil.generate_password(0,"hi",5)
        with self.assertRaises(Exception):
            passutil.generate_password(0,"hi","")
        with self.assertRaises(Exception):
            passutil.generate_password(0,"hi",set())
        with self.assertRaises(Exception):
            passutil.generate_password(0,"hi",[{65,66,67}])

class Test_API(unittest.TestCase):
    def test_1(self):
        self.assertEqual(type(passutil.SHA512_number),int)
        self.assertTrue(passutil.SHA512_number in [2,3])
        self.assertTrue(callable(passutil.generate_password))
        self.assertTrue(callable(passutil.charset_size))

if __name__ == '__main__':
    unittest.main()