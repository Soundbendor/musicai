import unittest
from musicai.structure.pitch import Pitch, Accidental, Step

class StepTest(unittest.TestCase):
    def test_Step_from_str(self):
        
        print("HI")

        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
        
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

