import unittest

from musicai.structure.note import Note, NoteType, NoteValue


class NoteTypeTest(unittest.TestCase):

    def test_def_NoteType(self):
        self.assertEqual(str(NoteType.from_float(0.25)), str(NoteType.QUARTER))
        self.assertEqual(str(NoteType.from_float(0.125)), str(NoteType.EIGHTH))
        self.assertEqual(str(NoteType.from_float(8)), str(NoteType.LARGE))
        self.assertEqual(str(NoteType.from_float(0.000244141)), str(NoteType.FOUR_THOUSAND_NINETY_SIXTH))
        # TODO add more

        # invalid values
        # TODO


