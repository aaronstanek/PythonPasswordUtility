import unittest
import sys
from unittest.case import TestCase
sys.path.append("../src")
import passutil
import passutil.pu as pu
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

if __name__ == '__main__':
    unittest.main()