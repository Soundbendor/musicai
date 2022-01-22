import operator
import unittest
from musicai.structure.pitch import Pitch, Accidental, Step


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

        # invalid values
        # self.assertRaises(ValueError, str, Accidental.)

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

        # invalid values
        # self.assertRaises(ValueError, str, Accidental.)




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

