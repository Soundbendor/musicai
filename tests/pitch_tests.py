import operator
import unittest
from musicai.structure.pitch import Pitch, Accidental, Step, Octave


class StepTest(unittest.TestCase):
    def test_int_override(self):
        # valid values
        self.assertEqual(int(Step.C), 0)
        self.assertEqual(int(Step.D), 2)
        self.assertEqual(int(Step.E), 4)
        self.assertEqual(int(Step.F), 5)
        self.assertEqual(int(Step.G), 7)
        self.assertEqual(int(Step.A), 9)
        self.assertEqual(int(Step.B), 11)

    def test_str_override(self):
        # valid values
        self.assertEqual(str(Step.C), 'C')
        self.assertEqual(str(Step.D), 'D')
        self.assertEqual(str(Step.E), 'E')
        self.assertEqual(str(Step.F), 'F')
        self.assertEqual(str(Step.G), 'G')
        self.assertEqual(str(Step.A), 'A')
        self.assertEqual(str(Step.B), 'B')

    def test_repr_override(self):
        # valid values
        self.assertEqual(repr(Step.C), '<Step(C)>')
        self.assertEqual(repr(Step.D), '<Step(D)>')
        self.assertEqual(repr(Step.E), '<Step(E)>')
        self.assertEqual(repr(Step.F), '<Step(F)>')
        self.assertEqual(repr(Step.G), '<Step(G)>')
        self.assertEqual(repr(Step.A), '<Step(A)>')
        self.assertEqual(repr(Step.B), '<Step(B)>')

    def test_add_override(self):
        # valid values for step-step addition
        self.assertEqual(Step.C + Step.C, 0)
        self.assertEqual(Step.C + Step.D, 2)
        self.assertEqual(Step.C + Step.E, 4)
        self.assertEqual(Step.C + Step.F, 5)
        self.assertEqual(Step.C + Step.G, 7)
        self.assertEqual(Step.C + Step.A, 9)
        self.assertEqual(Step.C + Step.B, 11)

        self.assertEqual(Step.D + Step.C, 2)
        self.assertEqual(Step.D + Step.D, 4)
        self.assertEqual(Step.D + Step.E, 6)
        self.assertEqual(Step.D + Step.F, 7)
        self.assertEqual(Step.D + Step.G, 9)
        self.assertEqual(Step.D + Step.A, 11)
        self.assertEqual(Step.D + Step.B, 13)

        self.assertEqual(Step.E + Step.C, 4)
        self.assertEqual(Step.E + Step.D, 6)
        self.assertEqual(Step.E + Step.E, 8)
        self.assertEqual(Step.E + Step.F, 9)
        self.assertEqual(Step.E + Step.G, 11)
        self.assertEqual(Step.E + Step.A, 13)
        self.assertEqual(Step.E + Step.B, 15)

        self.assertEqual(Step.F + Step.C, 5)
        self.assertEqual(Step.F + Step.D, 7)
        self.assertEqual(Step.F + Step.E, 9)
        self.assertEqual(Step.F + Step.F, 10)
        self.assertEqual(Step.F + Step.G, 12)
        self.assertEqual(Step.F + Step.A, 14)
        self.assertEqual(Step.F + Step.B, 16)

        self.assertEqual(Step.G + Step.C, 7)
        self.assertEqual(Step.G + Step.D, 9)
        self.assertEqual(Step.G + Step.E, 11)
        self.assertEqual(Step.G + Step.F, 12)
        self.assertEqual(Step.G + Step.G, 14)
        self.assertEqual(Step.G + Step.A, 16)
        self.assertEqual(Step.G + Step.B, 18)

        self.assertEqual(Step.A + Step.C, 9)
        self.assertEqual(Step.A + Step.D, 11)
        self.assertEqual(Step.A + Step.E, 13)
        self.assertEqual(Step.A + Step.F, 14)
        self.assertEqual(Step.A + Step.G, 16)
        self.assertEqual(Step.A + Step.A, 18)
        self.assertEqual(Step.A + Step.B, 20)

        self.assertEqual(Step.B + Step.C, 11)
        self.assertEqual(Step.B + Step.D, 13)
        self.assertEqual(Step.B + Step.E, 15)
        self.assertEqual(Step.B + Step.F, 16)
        self.assertEqual(Step.B + Step.G, 18)
        self.assertEqual(Step.B + Step.A, 20)
        self.assertEqual(Step.B + Step.B, 22)

        # valid values for step-nonstep addition
        self.assertEqual(Step.C + 0, 0)
        self.assertEqual(Step.C + 5, 5)
        self.assertEqual(Step.C + 0.0, 0)
        self.assertEqual(Step.C + 5.0, 5)

        self.assertEqual(Step.D + 0, 2)
        self.assertEqual(Step.D + 5, 7)
        self.assertEqual(Step.D + 0.0, 2)
        self.assertEqual(Step.D + 5.0, 7)

        self.assertEqual(Step.E + 0, 4)
        self.assertEqual(Step.E + 5, 9)
        self.assertEqual(Step.E + 0.0, 4)
        self.assertEqual(Step.E + 5.0, 9)

        self.assertEqual(Step.F + 0, 5)
        self.assertEqual(Step.F + 5, 10)
        self.assertEqual(Step.F + 0.0, 5)
        self.assertEqual(Step.F + 5.0, 10)

        self.assertEqual(Step.G + 0, 7)
        self.assertEqual(Step.G + 5, 12)
        self.assertEqual(Step.G + 0.0, 7)
        self.assertEqual(Step.G + 5.0, 12)

        self.assertEqual(Step.A + 0, 9)
        self.assertEqual(Step.A + 5, 14)
        self.assertEqual(Step.A + 0.0, 9)
        self.assertEqual(Step.A + 5.0, 14)

        self.assertEqual(Step.B + 0, 11)
        self.assertEqual(Step.B + 5, 16)
        self.assertEqual(Step.B + 0.0, 11)
        self.assertEqual(Step.B + 5.0, 16)

        # invalid values
        self.assertRaises(TypeError, operator.add, Step.C, 'string')
        self.assertRaises(TypeError, operator.add, Step.D, 'string')
        self.assertRaises(TypeError, operator.add, Step.E, 'string')
        self.assertRaises(TypeError, operator.add, Step.F, 'string')
        self.assertRaises(TypeError, operator.add, Step.G, 'string')
        self.assertRaises(TypeError, operator.add, Step.A, 'string')
        self.assertRaises(TypeError, operator.add, Step.B, 'string')

    def test_sub_override(self):
        # valid values for step-step subtraction
        self.assertEqual(Step.C - Step.C, 0)
        self.assertEqual(Step.C - Step.D, -2)
        self.assertEqual(Step.C - Step.E, -4)
        self.assertEqual(Step.C - Step.F, -5)
        self.assertEqual(Step.C - Step.G, -7)
        self.assertEqual(Step.C - Step.A, -9)
        self.assertEqual(Step.C - Step.B, -11)

        self.assertEqual(Step.D - Step.C, 2)
        self.assertEqual(Step.D - Step.D, 0)
        self.assertEqual(Step.D - Step.E, -2)
        self.assertEqual(Step.D - Step.F, -3)
        self.assertEqual(Step.D - Step.G, -5)
        self.assertEqual(Step.D - Step.A, -7)
        self.assertEqual(Step.D - Step.B, -9)

        self.assertEqual(Step.E - Step.C, 4)
        self.assertEqual(Step.E - Step.D, 2)
        self.assertEqual(Step.E - Step.E, 0)
        self.assertEqual(Step.E - Step.F, -1)
        self.assertEqual(Step.E - Step.G, -3)
        self.assertEqual(Step.E - Step.A, -5)
        self.assertEqual(Step.E - Step.B, -7)

        self.assertEqual(Step.F - Step.C, 5)
        self.assertEqual(Step.F - Step.D, 3)
        self.assertEqual(Step.F - Step.E, 1)
        self.assertEqual(Step.F - Step.F, 0)
        self.assertEqual(Step.F - Step.G, -2)
        self.assertEqual(Step.F - Step.A, -4)
        self.assertEqual(Step.F - Step.B, -6)

        self.assertEqual(Step.G - Step.C, 7)
        self.assertEqual(Step.G - Step.D, 5)
        self.assertEqual(Step.G - Step.E, 3)
        self.assertEqual(Step.G - Step.F, 2)
        self.assertEqual(Step.G - Step.G, 0)
        self.assertEqual(Step.G - Step.A, -2)
        self.assertEqual(Step.G - Step.B, -4)

        self.assertEqual(Step.A - Step.C, 9)
        self.assertEqual(Step.A - Step.D, 7)
        self.assertEqual(Step.A - Step.E, 5)
        self.assertEqual(Step.A - Step.F, 4)
        self.assertEqual(Step.A - Step.G, 2)
        self.assertEqual(Step.A - Step.A, 0)
        self.assertEqual(Step.A - Step.B, -2)

        self.assertEqual(Step.B - Step.C, 11)
        self.assertEqual(Step.B - Step.D, 9)
        self.assertEqual(Step.B - Step.E, 7)
        self.assertEqual(Step.B - Step.F, 6)
        self.assertEqual(Step.B - Step.G, 4)
        self.assertEqual(Step.B - Step.A, 2)
        self.assertEqual(Step.B - Step.B, 0)

        # valid values for step-nonstep subtraction
        self.assertEqual(Step.C - 0, 0)
        self.assertEqual(Step.C - 5, -5)
        self.assertEqual(Step.C - 0.0, 0)
        self.assertEqual(Step.C - 5.0, -5)

        self.assertEqual(Step.D - 0, 2)
        self.assertEqual(Step.D - 5, -3)
        self.assertEqual(Step.D - 0.0, 2)
        self.assertEqual(Step.D - 5.0, -3)

        self.assertEqual(Step.E - 0, 4)
        self.assertEqual(Step.E - 5, -1)
        self.assertEqual(Step.E - 0.0, 4)
        self.assertEqual(Step.E - 5.0, -1)

        self.assertEqual(Step.F - 0, 5)
        self.assertEqual(Step.F - 5, 0)
        self.assertEqual(Step.F - 0.0, 5)
        self.assertEqual(Step.F - 5.0, 0)

        self.assertEqual(Step.G - 0, 7)
        self.assertEqual(Step.G - 5, 2)
        self.assertEqual(Step.G - 0.0, 7)
        self.assertEqual(Step.G - 5.0, 2)

        self.assertEqual(Step.A - 0, 9)
        self.assertEqual(Step.A - 5, 4)
        self.assertEqual(Step.A - 0.0, 9)
        self.assertEqual(Step.A - 5.0, 4)

        self.assertEqual(Step.B - 0, 11)
        self.assertEqual(Step.B - 5, 6)
        self.assertEqual(Step.B - 0.0, 11)
        self.assertEqual(Step.B - 5.0, 6)

        # invalid values
        self.assertRaises(TypeError, operator.sub, Step.C, 'string')
        self.assertRaises(TypeError, operator.sub, Step.D, 'string')
        self.assertRaises(TypeError, operator.sub, Step.E, 'string')
        self.assertRaises(TypeError, operator.sub, Step.F, 'string')
        self.assertRaises(TypeError, operator.sub, Step.G, 'string')
        self.assertRaises(TypeError, operator.sub, Step.A, 'string')
        self.assertRaises(TypeError, operator.sub, Step.B, 'string')

    def test_mod_override(self):
        # valid values for step-step modulo
        self.assertEqual(Step.C % Step.D, 0)
        self.assertEqual(Step.C % Step.E, 0)
        self.assertEqual(Step.C % Step.F, 0)
        self.assertEqual(Step.C % Step.G, 0)
        self.assertEqual(Step.C % Step.A, 0)
        self.assertEqual(Step.C % Step.B, 0)

        self.assertEqual(Step.D % Step.D, 0)
        self.assertEqual(Step.D % Step.E, 2)
        self.assertEqual(Step.D % Step.F, 2)
        self.assertEqual(Step.D % Step.G, 2)
        self.assertEqual(Step.D % Step.A, 2)
        self.assertEqual(Step.D % Step.B, 2)

        self.assertEqual(Step.E % Step.D, 0)
        self.assertEqual(Step.E % Step.E, 0)
        self.assertEqual(Step.E % Step.F, 4)
        self.assertEqual(Step.E % Step.G, 4)
        self.assertEqual(Step.E % Step.A, 4)
        self.assertEqual(Step.E % Step.B, 4)

        self.assertEqual(Step.F % Step.D, 1)
        self.assertEqual(Step.F % Step.E, 1)
        self.assertEqual(Step.F % Step.F, 0)
        self.assertEqual(Step.F % Step.G, 5)
        self.assertEqual(Step.F % Step.A, 5)
        self.assertEqual(Step.F % Step.B, 5)

        self.assertEqual(Step.G % Step.D, 1)
        self.assertEqual(Step.G % Step.E, 3)
        self.assertEqual(Step.G % Step.F, 2)
        self.assertEqual(Step.G % Step.G, 0)
        self.assertEqual(Step.G % Step.A, 7)
        self.assertEqual(Step.G % Step.B, 7)

        self.assertEqual(Step.A % Step.D, 1)
        self.assertEqual(Step.A % Step.E, 1)
        self.assertEqual(Step.A % Step.F, 4)
        self.assertEqual(Step.A % Step.G, 2)
        self.assertEqual(Step.A % Step.A, 0)
        self.assertEqual(Step.A % Step.B, 9)

        self.assertEqual(Step.B % Step.D, 1)
        self.assertEqual(Step.B % Step.E, 3)
        self.assertEqual(Step.B % Step.F, 1)
        self.assertEqual(Step.B % Step.G, 4)
        self.assertEqual(Step.B % Step.A, 2)
        self.assertEqual(Step.B % Step.B, 0)

        # valid values for step-nonstep modulo
        self.assertEqual(Step.C % 1, 0)
        self.assertEqual(Step.C % 2, 0)
        self.assertEqual(Step.C % 1.0, 0)
        self.assertEqual(Step.C % 2.0, 0)

        self.assertEqual(Step.D % 1, 0)
        self.assertEqual(Step.D % 2, 0)
        self.assertEqual(Step.D % 1.0, 0)
        self.assertEqual(Step.D % 2.0, 0)

        self.assertEqual(Step.E % 1, 0)
        self.assertEqual(Step.E % 2, 0)
        self.assertEqual(Step.E % 1.0, 0)
        self.assertEqual(Step.E % 2.0, 0)

        self.assertEqual(Step.F % 1, 0)
        self.assertEqual(Step.F % 2, 1)
        self.assertEqual(Step.F % 1.0, 0)
        self.assertEqual(Step.F % 2.0, 1)

        self.assertEqual(Step.G % 1, 0)
        self.assertEqual(Step.G % 2, 1)
        self.assertEqual(Step.G % 1.0, 0)
        self.assertEqual(Step.G % 2.0, 1)

        self.assertEqual(Step.A % 1, 0)
        self.assertEqual(Step.A % 2, 1)
        self.assertEqual(Step.A % 1.0, 0)
        self.assertEqual(Step.A % 2.0, 1)

        self.assertEqual(Step.B % 1, 0)
        self.assertEqual(Step.B % 2, 1)
        self.assertEqual(Step.B % 1.0, 0)
        self.assertEqual(Step.B % 2.0, 1)

        # invalid values
        self.assertRaises(ZeroDivisionError, operator.mod, Step.C, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.D, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.E, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.F, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.G, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.A, Step.C)
        self.assertRaises(ZeroDivisionError, operator.mod, Step.B, Step.C)

        self.assertRaises(TypeError, operator.mod, Step.C, 'string')
        self.assertRaises(TypeError, operator.mod, Step.D, 'string')
        self.assertRaises(TypeError, operator.mod, Step.E, 'string')
        self.assertRaises(TypeError, operator.mod, Step.F, 'string')
        self.assertRaises(TypeError, operator.mod, Step.G, 'string')
        self.assertRaises(TypeError, operator.mod, Step.A, 'string')
        self.assertRaises(TypeError, operator.mod, Step.B, 'string')

    def test_Step_next(self):
        # valid values
        self.assertEqual(Step.C.next(), Step.D)
        self.assertEqual(Step.D.next(), Step.E)
        self.assertEqual(Step.E.next(), Step.F)
        self.assertEqual(Step.F.next(), Step.G)
        self.assertEqual(Step.G.next(), Step.A)
        self.assertEqual(Step.A.next(), Step.B)
        self.assertEqual(Step.B.next(), Step.C)

    def test_Step_prev(self):
        # valid values
        self.assertEqual(Step.C.prev(), Step.B)
        self.assertEqual(Step.D.prev(), Step.C)
        self.assertEqual(Step.E.prev(), Step.D)
        self.assertEqual(Step.F.prev(), Step.E)
        self.assertEqual(Step.G.prev(), Step.F)
        self.assertEqual(Step.A.prev(), Step.G)
        self.assertEqual(Step.B.prev(), Step.A)

    def test_Step_diff(self):
        # valid values
        self.assertEqual(Step.C.diff(Step.C), 0)
        self.assertEqual(Step.C.diff(Step.D), 1)
        self.assertEqual(Step.C.diff(Step.E), 2)
        self.assertEqual(Step.C.diff(Step.F), 3)
        self.assertEqual(Step.C.diff(Step.G), 4)
        self.assertEqual(Step.C.diff(Step.A), 5)
        self.assertEqual(Step.C.diff(Step.B), 6)

        self.assertEqual(Step.D.diff(Step.C), -1)
        self.assertEqual(Step.D.diff(Step.D), 0)
        self.assertEqual(Step.D.diff(Step.E), 1)
        self.assertEqual(Step.D.diff(Step.F), 2)
        self.assertEqual(Step.D.diff(Step.G), 3)
        self.assertEqual(Step.D.diff(Step.A), 4)
        self.assertEqual(Step.D.diff(Step.B), 5)

        self.assertEqual(Step.E.diff(Step.C), -2)
        self.assertEqual(Step.E.diff(Step.D), -1)
        self.assertEqual(Step.E.diff(Step.E), 0)
        self.assertEqual(Step.E.diff(Step.F), 1)
        self.assertEqual(Step.E.diff(Step.G), 2)
        self.assertEqual(Step.E.diff(Step.A), 3)
        self.assertEqual(Step.E.diff(Step.B), 4)

        self.assertEqual(Step.F.diff(Step.C), -3)
        self.assertEqual(Step.F.diff(Step.D), -2)
        self.assertEqual(Step.F.diff(Step.E), -1)
        self.assertEqual(Step.F.diff(Step.F), 0)
        self.assertEqual(Step.F.diff(Step.G), 1)
        self.assertEqual(Step.F.diff(Step.A), 2)
        self.assertEqual(Step.F.diff(Step.B), 3)

        self.assertEqual(Step.G.diff(Step.C), -4)
        self.assertEqual(Step.G.diff(Step.D), -3)
        self.assertEqual(Step.G.diff(Step.E), -2)
        self.assertEqual(Step.G.diff(Step.F), -1)
        self.assertEqual(Step.G.diff(Step.G), 0)
        self.assertEqual(Step.G.diff(Step.A), 1)
        self.assertEqual(Step.G.diff(Step.B), 2)

        self.assertEqual(Step.A.diff(Step.C), -5)
        self.assertEqual(Step.A.diff(Step.D), -4)
        self.assertEqual(Step.A.diff(Step.E), -3)
        self.assertEqual(Step.A.diff(Step.F), -2)
        self.assertEqual(Step.A.diff(Step.G), -1)
        self.assertEqual(Step.A.diff(Step.A), 0)
        self.assertEqual(Step.A.diff(Step.B), 1)

        self.assertEqual(Step.B.diff(Step.C), -6)
        self.assertEqual(Step.B.diff(Step.D), -5)
        self.assertEqual(Step.B.diff(Step.E), -4)
        self.assertEqual(Step.B.diff(Step.F), -3)
        self.assertEqual(Step.B.diff(Step.G), -2)
        self.assertEqual(Step.B.diff(Step.A), -1)
        self.assertEqual(Step.B.diff(Step.B), 0)

        # invalid values
        self.assertRaises(TypeError, Step.C.diff, 'string')

    def test_Step_has_name(self):
        # valid values
        self.assertEqual(Step.has_name('C'), True)
        self.assertEqual(Step.has_name('D'), True)
        self.assertEqual(Step.has_name('E'), True)
        self.assertEqual(Step.has_name('F'), True)
        self.assertEqual(Step.has_name('G'), True)
        self.assertEqual(Step.has_name('A'), True)
        self.assertEqual(Step.has_name('B'), True)

        self.assertEqual(Step.has_name('string'), False)

    def test_Step_has_value(self):
        # valid values
        self.assertEqual(Step.has_value(0), True)
        self.assertEqual(Step.has_value(2), True)
        self.assertEqual(Step.has_value(4), True)
        self.assertEqual(Step.has_value(5), True)
        self.assertEqual(Step.has_value(7), True)
        self.assertEqual(Step.has_value(9), True)
        self.assertEqual(Step.has_value(11), True)
        self.assertEqual(Step.has_value(-1), True)

        self.assertEqual(Step.has_value(1), False)
        self.assertEqual(Step.has_value(3), False)
        self.assertEqual(Step.has_value(6), False)
        self.assertEqual(Step.has_value(8), False)
        self.assertEqual(Step.has_value(10), False)

    def test_Step_from_str(self):
        # valid values
        self.assertEqual(Step.from_str('C'), Step.C)
        self.assertEqual(Step.from_str('c'), Step.C)
        self.assertEqual(Step.from_str(' C '), Step.C)
        self.assertEqual(Step.from_str('do'), Step.C)
        self.assertEqual(Step.from_str('Pa'), Step.C)

        # invalid values
        self.assertRaises(ValueError, Step.from_str, 'C♭')
        self.assertRaises(ValueError, Step.from_str, 'foo')


class AccidentalTest(unittest.TestCase):
    def test_abc_Accidental(self):
        # valid values
        self.assertEqual(Accidental.from_abc(''), Accidental.NONE)
        self.assertEqual(Accidental.from_abc('_'), Accidental.FLAT)
        self.assertEqual(Accidental.from_abc('^'), Accidental.SHARP)
        self.assertEqual(Accidental.from_abc('='), Accidental.NATURAL)
        self.assertEqual(Accidental.from_abc('__'), Accidental.DOUBLE_FLAT)
        self.assertEqual(Accidental.from_abc('^^'), Accidental.DOUBLE_SHARP)
        self.assertEqual(Accidental.from_abc('=_'), Accidental.NATURAL_FLAT)
        self.assertEqual(Accidental.from_abc('=^'), Accidental.NATURAL_SHARP)
        self.assertEqual(Accidental.from_abc('___'), Accidental.TRIPLE_FLAT)
        self.assertEqual(Accidental.from_abc('^^^'), Accidental.TRIPLE_SHARP)

        # invalid values
        self.assertRaises(ValueError, Accidental.from_abc, '^=')
        self.assertRaises(ValueError, Accidental.from_abc, '_=')
        self.assertRaises(ValueError, Accidental.from_abc, 'foo')

    def test_float_override(self):
        # valid values
        self.assertEqual(float(Accidental.TRIPLE_FLAT), -3.0)
        self.assertEqual(float(Accidental.DOUBLE_FLAT), -2.0)
        self.assertEqual(float(Accidental.FLAT_FLAT), -2.0)
        self.assertEqual(float(Accidental.FLAT), -1.0)
        self.assertEqual(float(Accidental.NATURAL_FLAT), -1.0)
        self.assertEqual(float(Accidental.THREE_QUARTERS_FLAT), -0.75)
        self.assertEqual(float(Accidental.QUARTER_FLAT), -0.25)
        self.assertEqual(float(Accidental.NONE), 0.0)
        self.assertEqual(float(Accidental.NATURAL), 0.0)
        # self.assertEqual(float(Accidental.NATURAL_NATURAL), '♮')
        self.assertEqual(float(Accidental.QUARTER_SHARP), 0.25)
        self.assertEqual(float(Accidental.THREE_QUARTERS_SHARP), 0.75)
        self.assertEqual(float(Accidental.SHARP), 1.0)
        self.assertEqual(float(Accidental.NATURAL_SHARP), 1.0)
        self.assertEqual(float(Accidental.DOUBLE_SHARP), 2.0)
        self.assertEqual(float(Accidental.SHARP_SHARP), 2.0)
        self.assertEqual(float(Accidental.TRIPLE_SHARP), 3.0)

    def test_str_override(self):
        # valid values
        self.assertEqual(str(Accidental.TRIPLE_FLAT), '♭𝄫')
        self.assertEqual(str(Accidental.DOUBLE_FLAT), '𝄫')
        self.assertEqual(str(Accidental.FLAT_FLAT), '♭♭')
        self.assertEqual(str(Accidental.FLAT), '♭')
        self.assertEqual(str(Accidental.NATURAL_FLAT), '♮♭')
        self.assertEqual(str(Accidental.THREE_QUARTERS_FLAT), '𝄳♭')
        self.assertEqual(str(Accidental.QUARTER_FLAT), '𝄳')
        self.assertEqual(str(Accidental.NONE), '')
        self.assertEqual(str(Accidental.NATURAL), '♮')
        # self.assertEqual(str(Accidental.NATURAL_NATURAL), '♮')
        self.assertEqual(str(Accidental.QUARTER_SHARP), '𝄲')
        self.assertEqual(str(Accidental.THREE_QUARTERS_SHARP), '𝄲♯')
        self.assertEqual(str(Accidental.SHARP), '♯')
        self.assertEqual(str(Accidental.NATURAL_SHARP), '♮♯')
        self.assertEqual(str(Accidental.DOUBLE_SHARP), '𝄪')
        self.assertEqual(str(Accidental.SHARP_SHARP), '♯♯')
        self.assertEqual(str(Accidental.TRIPLE_SHARP), '♯𝄪')




class OctaveTest(unittest.TestCase):
    def test_int_override(self):
        # valid values
        self.assertEqual(int(Octave.NONE), -2)
        self.assertEqual(int(Octave.SUB_SUB_CONTRA), -1)
        self.assertEqual(int(Octave.TWO_LINE), 5)
        self.assertEqual(int(Octave.SEVEN_LINE), 10)

    def test_str_override(self):
        # valid values
        self.assertEqual(str(Octave.NONE), '-2')
        self.assertEqual(str(Octave.SUB_SUB_CONTRA), '-1')
        self.assertEqual(str(Octave.TWO_LINE), '5')
        self.assertEqual(str(Octave.SEVEN_LINE), '10')

    def test_repr_override(self):
        # valid values
        self.assertEqual(repr(Octave.NONE), '<Octave(NONE)>')
        self.assertEqual(repr(Octave.SUB_SUB_CONTRA), '<Octave(SUB_SUB_CONTRA)>')
        self.assertEqual(repr(Octave.TWO_LINE), '<Octave(TWO_LINE)>')
        self.assertEqual(repr(Octave.SEVEN_LINE), '<Octave(SEVEN_LINE)>')

    def test_add_override(self):
        # valid values
        self.assertEqual(Octave.NONE + Octave.NONE, -4)
        self.assertEqual(Octave.SUB_SUB_CONTRA + (-1), -2)
        self.assertEqual(Octave.TWO_LINE + Octave.FOUR_LINE, 12)
        self.assertEqual(Octave.SEVEN_LINE + Octave.SIX_LINE, 19)

        # invalid value
        self.assertRaises(TypeError, operator.add, Octave.TWO_LINE, 'string')

    def test_radd_override(self):
        # valid values
        self.assertEqual(-2 + Octave.NONE, -4)
        self.assertEqual(-1 + Octave.SUB_SUB_CONTRA, -2)
        self.assertEqual(5 + Octave.FOUR_LINE, 12)
        self.assertEqual(10 + Octave.SIX_LINE, 19)

        # invalid value
        # self.assertRaises(TypeError, operator.__radd__, Octave.TWO_LINE, 'string')

    def test_sub_override(self):
        # valid values
        self.assertEqual(Octave.NONE - Octave.NONE, 0)
        self.assertEqual(Octave.SUB_SUB_CONTRA - Octave.SUB_SUB_CONTRA, 0)
        self.assertEqual(Octave.FIVE_LINE - 7, 1)
        self.assertEqual(Octave.SEVEN_LINE - 9, 1)

        # invalid value
        self.assertRaises(TypeError, operator.sub, Octave.TWO_LINE, 'string')

    def test_sub_override(self):
        # valid values
        self.assertEqual(Octave.NONE - Octave.NONE, 0)
        self.assertEqual(Octave.SUB_SUB_CONTRA - Octave.SUB_SUB_CONTRA, 0)
        self.assertEqual(Octave.FIVE_LINE - 7, 1)
        self.assertEqual(Octave.SEVEN_LINE - 9, 1)

        # invalid value
        self.assertRaises(TypeError, operator.sub, Octave.TWO_LINE, 'string')

    def test_rsub_override(self):
        # valid values
        self.assertEqual(-2 - Octave.NONE, 0)
        self.assertEqual(-1 - Octave.SUB_SUB_CONTRA, 0)
        self.assertEqual(9 - Octave.SEVEN_LINE, -1)

        # invalid value
        # self.assertRaises(TypeError, operator.rsub, Octave.TWO_LINE, 'string')

    def test_mul_override(self):
        # valid values
        self.assertEqual(Octave.NONE * Octave.NONE, 4)
        self.assertEqual(Octave.SUB_SUB_CONTRA * -1, 1)
        self.assertEqual(Octave.SEVEN_LINE * 9, 90)

    def test_rmul_override(self):
        # valid values
        self.assertEqual(-2 * Octave.NONE, 4)
        self.assertEqual(-1 * Octave.SUB_SUB_CONTRA, 1)
        self.assertEqual(9 * Octave.SEVEN_LINE, 90)

    def test_truediv_override(self):
        # valid values
        self.assertEqual(Octave.NONE / Octave.NONE, 1)
        self.assertEqual(Octave.SUB_SUB_CONTRA / -1, 1)
        self.assertEqual(Octave.SEVEN_LINE / 9, 10/9)

        # invalid value
        self.assertRaises(TypeError, operator.truediv, Octave.TWO_LINE, 'string')

    def test_rtruediv_override(self):
        # valid values
        self.assertEqual(-2 / Octave.NONE, 1)
        self.assertEqual(-1 / Octave.SUB_SUB_CONTRA, 1)
        self.assertEqual(9 / Octave.SEVEN_LINE, 9/10)

        # invalid value
        # self.assertRaises(TypeError, operator.rmul, Octave.TWO_LINE, 'string')

    def test_from_int(self):
        # valid values
        self.assertEqual(Octave.from_int(-2), Octave.NONE)
        self.assertEqual(Octave.from_int(4), Octave.ONE_LINE)
        self.assertEqual(Octave.from_int(10), Octave.SEVEN_LINE)

        # invalid value
        self.assertRaises(ValueError, Octave.from_int, -3)
        self.assertRaises(ValueError, Octave.from_int, 11)


class PitchTest(unittest.TestCase):

    def test_from_midi(self):
        self.assertEqual(str(Pitch.from_midi(60)), 'C4')
        self.assertEqual(str(Pitch.from_midi(62)), 'D4')
        self.assertEqual(str(Pitch.from_midi(64)), 'E4')
        self.assertEqual(str(Pitch.from_midi(65)), 'F4')
        self.assertEqual(str(Pitch.from_midi(67)), 'G4')
        self.assertEqual(str(Pitch.from_midi(69)), 'A4')
        self.assertEqual(str(Pitch.from_midi(71)), 'B4')

        # invalid values
        # TODO

