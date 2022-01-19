import unittest
from musicai.structure.pitch import Pitch, Accidental, Step

class StepTest(unittest.TestCase):
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

