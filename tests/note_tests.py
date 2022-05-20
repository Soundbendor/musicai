import operator
import unittest

from musicai.structure.note import NoteType, NoteValue, DotType, Ratio, TupletType


class NoteTypeTest(unittest.TestCase):
    def test_str_override(self):
        # valid values
        self.assertEqual(str(NoteType.LARGE), 'Large')
        self.assertEqual(str(NoteType.SIXTY_FOURTH), 'Sixty Fourth')
        self.assertEqual(str(NoteType.FOUR_THOUSAND_NINETY_SIXTH), 'Four Thousand Ninety Sixth')

    def test_repr_override(self):
        # valid values
        self.assertEqual(repr(NoteType.LARGE), '<NoteType(LARGE) 8.0>')
        self.assertEqual(repr(NoteType.SIXTEENTH), '<NoteType(SIXTEENTH) 0.0625>')
        self.assertEqual(repr(NoteType.FOUR_THOUSAND_NINETY_SIXTH), '<NoteType(FOUR_THOUSAND_NINETY_SIXTH) 0.000244141>'
                         )

    def test_from_float(self):
        # valid values
        self.assertEqual(NoteType.from_float(0.25), NoteType.QUARTER)
        self.assertEqual(NoteType.from_float(0.125), NoteType.EIGHTH)
        self.assertEqual(NoteType.from_float(8), NoteType.LARGE)
        self.assertEqual(NoteType.from_float(0.000244141), NoteType.FOUR_THOUSAND_NINETY_SIXTH)
        self.assertEqual(NoteType.from_float(0), NoteType.NONE)

        # invalid values
        self.assertRaises(ValueError, NoteType.from_float, 0.047081)
        self.assertRaises(ValueError, NoteType.from_float, -8.0)
        self.assertRaises(TypeError, NoteType.from_float, 'string')

    def test_from_str(self):
        # valid values for abbreviation
        self.assertEqual(NoteType.from_str('large'), NoteType.LARGE)
        self.assertEqual(NoteType.from_str('double'), NoteType.DOUBLE)
        self.assertEqual(NoteType.from_str('32nd'), NoteType.THIRTY_SECOND)
        self.assertEqual(NoteType.from_str('4096th'), NoteType.FOUR_THOUSAND_NINETY_SIXTH)
        self.assertEqual(NoteType.from_str(''), NoteType.NONE)

        # valid values for name
        self.assertEqual(NoteType.from_str('thirty_second'), NoteType.THIRTY_SECOND)
        self.assertEqual(NoteType.from_str('sixty_fourth'), NoteType.SIXTY_FOURTH)
        self.assertEqual(NoteType.from_str('TWO_THOUSAND_FORTY_EIGHTH'), NoteType.TWO_THOUSAND_FORTY_EIGHTH)

        # valid values for note
        self.assertEqual(NoteType.from_str('\U0001D1B6'), NoteType.LARGE)
        self.assertEqual(NoteType.from_str('\U0001D162'), NoteType.THIRTY_SECOND)
        self.assertEqual(NoteType.from_str('\U0001D164'), NoteType.ONE_TWENTY_EIGHTH)

        # valid values for rest
        self.assertEqual(NoteType.from_str('\U0001D13A'), NoteType.LONG)
        self.assertEqual(NoteType.from_str('\U0001D13F'), NoteType.SIXTEENTH)
        self.assertEqual(NoteType.from_str('r4096th'), NoteType.FOUR_THOUSAND_NINETY_SIXTH)

        # invalid values
        self.assertRaises(ValueError, NoteType.from_str, 'string')
        self.assertRaises(ValueError, NoteType.from_str, 'random')

    def test_from_mxml(self):
        # valid values
        self.assertEqual(NoteType.from_mxml('1024th'), NoteType.ONE_THOUSAND_TWENTY_FOURTH)
        self.assertEqual(NoteType.from_mxml('64th'), NoteType.SIXTY_FOURTH)
        self.assertEqual(NoteType.from_mxml('half'), NoteType.HALF)
        self.assertEqual(NoteType.from_mxml('long'), NoteType.LONG)
        self.assertEqual(NoteType.from_mxml('maxima'), NoteType.LARGE)

        # invalid values
        self.assertWarns(UserWarning, NoteType.from_mxml, 'foo')

    def test_list(self):
        self.assertEqual(NoteType.list(), [0.0, 0.000244141, 0.000488281, 0.000976563, 0.001953125, 0.00390625,
                                           0.0078125, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0])


class DotTypeTest(unittest.TestCase):
    def test_str_override(self):
        # valid values
        self.assertEqual(str(DotType.NONE), 'None')
        self.assertEqual(str(DotType.THREE), 'Three')
        self.assertEqual(str(DotType.FOUR), 'Four')

    def test_repr_override(self):
        # valid values
        self.assertEqual(repr(DotType.NONE), '<DotType(NONE) 1.0>')
        self.assertEqual(repr(DotType.THREE), '<DotType(THREE) 1.875>')
        self.assertEqual(repr(DotType.FOUR), '<DotType(FOUR) 1.9375>')

    def test_mul_override(self):
        # valid values
        self.assertEqual(DotType.NONE * 1, 1.0)
        self.assertEqual(DotType.ONE * DotType.FOUR, 2.90625)
        self.assertEqual(DotType.TWO * DotType.THREE, 3.28125)
        self.assertEqual(DotType.FOUR * 0.3927, 0.76085625)

        # invalid values
        self.assertRaises(TypeError, operator.mul, DotType.ONE, 'string')

    def test_rmul_override(self):
        # valid values
        self.assertEqual(1 * DotType.NONE, 1.0)
        self.assertEqual(0.3927 * DotType.FOUR, 0.76085625)

        # invalid values
        # self.assertRaises(TypeError, operator.rmul, DotType.ONE, 'string')

    def test_list(self):
        self.assertEqual(DotType.list(), [0, 1, 2, 3, 4])


class TupletTypeTest(unittest.TestCase):
    def test_str_override(self):
        self.assertEqual(str(TupletType.REGULAR), 'Regular')
        self.assertEqual(str(TupletType((4, 3))), 'Quadruplet')
        self.assertEqual(str(TupletType.TREDECUPLET), 'Tredecuplet')

    def test_repr_override(self):
        self.assertEqual(repr(TupletType.REGULAR), '<TupletType(REGULAR) 1:1>')
        self.assertEqual(repr(TupletType((8, 6))), '<TupletType(OCTUPLET) 8:6>')
        self.assertEqual(repr(TupletType.TREDECUPLET), '<TupletType(TREDECUPLET) 13:8>')

    def test_list(self):
        self.assertEqual(TupletType.list(), [(1, 1), (3, 2), (2, 3), (4, 3), (5, 4), (6, 4), (7, 4), (8, 6), (9, 8),
                                             (10, 8), (11, 8), (12, 8), (13, 8)])


class RatioTest(unittest.TestCase):
    def test_str_override(self):
        self.assertEqual(str(Ratio()), '1:1')
        self.assertEqual(str(Ratio(Ratio(TupletType.NONUPLET))), '9:8')
        self.assertEqual(str(Ratio(TupletType.QUINTUPLET)), '5:4')
        self.assertEqual(str(Ratio((7, 48))), '7:48')

    def test_repr_override(self):
        self.assertEqual(repr(Ratio()), '<Ratio(1:1)>')
        self.assertEqual(repr(Ratio(Ratio(TupletType.DECUPLET))), '<Ratio(10:8)>')
        self.assertEqual(repr(Ratio(TupletType.SEXTUPLET)), '<Ratio(6:4)>')
        self.assertEqual(repr(Ratio((323, 11))), '<Ratio(323:11)>')

    def test_updated_tuplettype(self):
        t0 = Ratio()
        t0.normal = 55
        self.assertEqual(t0.custom, True)

        t1 = Ratio(TupletType.SEXTUPLET)
        t1.actual += 1
        self.assertEqual(t1.custom, False)

        t2 = Ratio((7, 6))
        t2.actual += 1
        self.assertEqual(t2.custom, False)

    def test_is_regular(self):
        self.assertEqual(Ratio().is_regular(), True)
        self.assertEqual(Ratio((1, 1)).is_regular(), True)
        self.assertEqual(Ratio(TupletType.REGULAR).is_regular(), True)

        self.assertEqual(Ratio((2, 3)).is_regular(), False)
        self.assertEqual(Ratio(Ratio(TupletType.QUINTUPLET)).is_regular(), False)
        self.assertEqual(Ratio(TupletType.NONUPLET).is_regular(), False)


class NoteValueTest(unittest.TestCase):
    def test_float_override(self):
        self.assertEqual(float(NoteValue(NoteType.LARGE, DotType.NONE, TupletType.REGULAR)), 8.0)
        self.assertEqual(float(NoteValue(NoteType.QUARTER, 1, (2, 3))), 0.5625)
        self.assertEqual(float(NoteValue(NoteType.FOUR_THOUSAND_NINETY_SIXTH, 4, Ratio((11, 6)))),
                         0.00025801264772727276)

    def test_int_override(self):
        self.assertEqual(int(NoteValue(NoteType.LARGE, DotType.NONE, TupletType.REGULAR)), 8)
        self.assertEqual(int(NoteValue(NoteType.QUARTER, 1, (2, 3))), 1)
        self.assertEqual(int(NoteValue(NoteType.FOUR_THOUSAND_NINETY_SIXTH, DotType.FOUR, Ratio((11, 6)))), 0)

    def test_str_override(self):
        self.assertEqual(str(NoteValue(NoteType.LARGE, DotType.NONE, TupletType.REGULAR)), '8.0')
        self.assertEqual(str(NoteValue(NoteType.QUARTER, 1, (2, 3))), '0.5625')
        self.assertEqual(str(NoteValue(NoteType.FOUR_THOUSAND_NINETY_SIXTH, DotType.FOUR, Ratio((11, 6)))),
                         '0.00025801264772727276')

    def test_repr_override(self):
        self.assertEqual(repr(NoteValue(NoteType.LARGE, DotType.NONE, TupletType.REGULAR)),
                         '<NoteValue(8.0) nt=Large, d=0, r=1:1>')
        self.assertEqual(repr(NoteValue(NoteType.QUARTER, 1, (2, 3))),
                         '<NoteValue(0.5625) nt=Quarter, d=1, r=2:3>')
        self.assertEqual(repr(NoteValue(NoteType.FOUR_THOUSAND_NINETY_SIXTH, DotType.FOUR, Ratio((11, 6)))),
                         '<NoteValue(0.00025801264772727276) nt=Four Thousand Ninety Sixth, d=4, r=11:6>')

    def test_lt_override(self):
        pass

    def test_le_override(self):
        pass

    def test_gt_override(self):
        pass

    def test_ge_override(self):
        pass

    def test_eq_override(self):
        pass

    def test_ne_override(self):
        pass

    def test_add_override(self):
        pass

    def test_radd_override(self):
        pass

    def test_sub_override(self):
        pass

    def test_rsub_override(self):
        pass

    def test_mul_override(self):
        pass

    def test_rmul_override(self):
        pass

    def test_truediv_override(self):
        pass

    def test_rtruediv_override(self):
        pass

    def test_floordiv_override(self):
        pass

    def test_rfloordiv_override(self):
        pass

    def test_mod_override(self):
        pass

    def test_rmod_override(self):
        pass

    def test_max(self):
        pass

    def test_min(self):
        pass

    def test_sum(self):
        pass

    def test_mean(self):
        pass

    def test_std(self):
        pass

    def test_exists(self):
        pass

    def test_find(self):
        pass
