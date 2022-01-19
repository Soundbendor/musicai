"""
Representation of a musical note or rest
"""
import logging
import re
from enum import Enum
from typing import Union
import numpy as np

from musicai.structure.attribute import StemType
from musicai.structure.pitch import Accidental, Pitch


# -------------
# NoteType enum
# -------------
class NoteType(Enum):
    """
    Representation the relative duration of a note or rest symbol
    """

    LARGE = (8.0, 'Large', '\U0001D1B6', '\U0001D13A')
    LONG = (4.0, 'Long', '\U0001D1B7', '\U0001D13A')
    DOUBLE = (2.0, 'Double', '\U0001D15C', '\U0001D13B')
    WHOLE = (1.0, 'Whole', '\U0001D15D', '\U0001D13B')
    HALF = (0.5, 'Half', '\U0001D15E', '\U0001D13C')
    QUARTER = (0.25, 'Quarter', '\U0001D15F', '\U0001D13D')
    EIGHTH = (0.125, '8th', '\U0001D160', '\U0001D13E')
    SIXTEENTH = (0.0625, '16th', '\U0001D161', '\U0001D13F')
    THIRTY_SECOND = (0.03125, '32nd', '\U0001D162', '\U0001D140')
    SIXTY_FOURTH = (0.015625, '64th', '\U0001D163', '\U0001D141')
    ONE_TWENTY_EIGHTH = (0.0078125, '128th', '\U0001D164', '\U0001D142')
    TWO_FIFTY_SIXTH = (0.00390625, '256th', '256th', 'r256th')
    FIVE_HUNDRED_TWELFTH = (0.001953125, '512th', '512th', 'r512th')
    ONE_THOUSAND_TWENTY_FOURTH = (0.000976563, '1024th', '1024th', 'r1024th')
    TWO_THOUSAND_FORTY_EIGHTH = (0.000488281, '2048th', '2048th', 'r2048th')
    FOUR_THOUSAND_NINETY_SIXTH = (0.000244141, '4096th', '4096th', 'r4096th')
    NONE = (0.0, '', '', '')

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.abbr = values[1]
        obj.note = values[2]
        obj.rest = values[3]
        obj._all_values = values
        return obj

    # --------
    # Override
    # --------
    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return self.name.title()

    def __repr__(self) -> str:
        return '<{self.__class__.__name__}({self.name}) {self.value}>'.format(self=self)

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def from_str(cls, lookup: str) -> 'NoteType':
        string = lookup.lower().strip()
        for nt in NoteType:
            if nt.abbr.lower() == string or nt.name.lower() == string or nt.note.lower() == string or nt.rest.lower() == string:
                return nt
        raise ValueError('Cannot find NoteType to match {0} of type {1}'.format(lookup, type(lookup)))

    @classmethod
    def from_float(cls, lookup: float) -> 'NoteType':
        for nt in NoteType:
            if nt.value == lookup:
                return nt
        raise ValueError('Cannot find NoteType to match {0} of type {1}'.format(lookup, type(lookup)))

    # @classmethod
    # def find(cls, lookup: Union[str, float]) -> 'NoteType':
    #     if isinstance(lookup, float):
    #         for nt in NoteType:
    #             if nt.value == lookup:
    #                 return nt
    #     elif isinstance(lookup, str):
    #         string = lookup.lower().strip()
    #         for nt in NoteType:
    #             if nt.abbr.lower() == string or nt.name.lower() == string or nt.note.lower() == string or nt.rest.lower() == string:
    #                 return nt
    #     raise ValueError('Cannot find NoteType to match {0} of type {1}'.format(lookup, type(lookup)))


# -------------
# DotType enum
# -------------
class DotType(Enum):
    """
    Enum to represent augmentation (dots) of a note or rest
    """

    NONE = 0, 1.0, ''
    ONE = 1, 1.5, '\u2024'
    TWO = 2, 1.75, '\u2025'
    THREE = 3, 1.875, '\u2026'
    FOUR = 4, 1.9375, '\u2026\u2024'

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.scalar = values[1]
        obj.symbol = values[2]
        obj._all_values = values
        return obj

    # ----------
    # Properties
    # ----------

    # --------
    # Override
    # --------
    def __mul__(self, other: float) -> float:
        return self.scalar * other

    def __rmul__(self, other: float) -> float:
        return other * self.scalar

    def __str__(self) -> str:
        return self.name.title()

    def __repr__(self) -> str:
        return '<{self.__class__.__name__}({self.name}) {self.value}>'.format(self=self)

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))



# ---------------
# TupletType enum
# ---------------
class TupletType(Enum):
    """
    Enum to represent irrational rhythms created by tuplets
    """

    REGULAR = (1, 1)
    TRIPLET = (3, 2)
    DUPLET = (2, 3)
    QUADRUPLET = (4, 3)
    QUINTUPLET = (5, 4)  # what about 5:2?
    SEXTUPLET = (6, 4)
    SEPTUPLET = (7, 4)  # what about 7:2?;
    OCTUPLET = (8, 6)
    NONUPLET = (9, 8)  # alternately 9:6?
    DECUPLET = (10, 8)
    UNDECUPLET = (11, 8)
    DODECUPLET = (12, 8)
    TREDECUPLET = (13, 8)

    # -----------
    # Constructor
    # -----------
    def __init__(self, actual, normal):
        self.actual = actual
        self.normal = normal
        self.symbol = str(actual) + ':' + str(normal)

    # --------
    # Override
    # --------
    def __str__(self) -> str:
        return self.name.title()

    def __repr__(self) -> str:
        return '<{self.__class__.__name__}({self.name}) {self.symbol}>'.format(self=self)

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: c.value, cls))


# -----------
# Ratio class
# -----------
class Ratio:
    """
    Class to represent a ratio
    """

    # -----------
    # Constructor
    # -----------
    def __init__(self, ratio: Union['Ratio', TupletType, tuple] = None):
        self.custom = False  # if True, ignore tuplettype
        if ratio is None:
            # default Tuplet
            self._normal_ = 1
            self._actual_ = 1
            self._update_tuplettype_()
        elif isinstance(ratio, Ratio):
            # from existing Tuplet
            self._normal_ = ratio.normal
            self._actual_ = ratio.actual
            self._update_tuplettype_()
        elif isinstance(ratio, TupletType):
            # from TupletType
            self._actual_ = ratio.actual
            self._normal_ = ratio.normal
            self._update_tuplettype_()
        elif type(ratio) == tuple and len(ratio) == 2:
            # from numeric tuple (actual, normal)
            self._actual_ = int(ratio[0])
            self._normal_ = int(ratio[1])
            self._update_tuplettype_()
        else:
            raise ValueError('Cannot create Tuplet from type {0}.'.format(type(ratio)))

    # ----------
    # Properties
    # ----------
    @property
    def normal(self) -> int:
        return self._normal_

    @normal.setter
    def normal(self, normal: int):
        self._normal_ = normal
        self._update_tuplettype_()

    @property
    def actual(self):
        return self._actual_

    @actual.setter
    def actual(self, actual):
        self._actual_ = actual
        self._update_tuplettype_()

    @property
    def tuplettype(self):
        return self._tuplettype_

    @tuplettype.setter
    def tuplettype(self, tuplettype):
        self._tuplettype_ = tuplettype
        # override actual and normal
        actual = self._tuplettype_.actual
        normal = self._tuplettype_.normal

    # --------
    # Override
    # --------
    def __str__(self):
        return self.symbol

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name}) {self.symbol}>'.format(self=self)

    # ---------
    # Methods
    # ---------
    def _update_tuplettype_(self):
        self.symbol = str(self.actual) + ':' + str(self.normal)
        if (self._actual_, self._normal_) not in TupletType.__members__:
            # custom ratio
            self._tuplettype_ = None
            self.custom = True
        else:
            # find tuplettype
            self._tuplettype_ = TupletType((self._actual_, self._normal_))
            self.custom = False

    def is_regular(self):
        if self._tuplettype_ is None:
            return self._actual_ == 1 and self._normal_ == 1
        return self._tuplettype_ is TupletType.REGULAR


# ---------------
# Notevalue class
# ---------------
class NoteValue:
    """
    Enum to represent the relative duration of a note or rest, taking into account augmentation and tuplets
    """
    _value_map_ = {}
    _NOTEVALUE_PRECISION_ = 20

    # -----------
    # Constructor
    # -----------
    def __init__(self, notetype, dots=DotType.NONE, ratio=None):
        self.notetype = notetype

        if isinstance(dots, (float, np.inexact, int, np.integer)):
            self.dots = DotType(dots)
        elif isinstance(dots, DotType):
            self.dots = dots
        else:
            raise ValueError('Cannot find DotType for {0}', dots)

        self.ratio = Ratio(ratio)
        self._value_ = self.notetype.value * self.dots * self.ratio.normal / self.ratio.actual

    # ----------
    # Properties
    # ----------
    @property
    def value(self):
        if self.ratio is None:
            return self.notetype.value * self.dots
        else:
            return (self.notetype.value * self.dots) * self.ratio.normal / self.ratio.actual

    @value.setter
    def value(self, value):
        # TODO : dynamically set value
        # self._value_ = value
        pass

    @property
    def note(self):
        return self.notetype.note

    @property
    def rest(self):
        return self.notetype.rest

    # --------
    # Override
    # --------
    def __float__(self):
        return self.value

    def __int__(self):
        return round(self.value)

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.value}) nt={self.notetype}, d={self.dots.value}, r={self.ratio}>'

    def __lt__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value < other
        elif isinstance(other, NoteValue):
            return self.value < other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __le__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value <= other
        elif isinstance(other, (NoteValue, NoteType)):
            return self.value <= other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __gt__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value > other
        elif isinstance(other, NoteValue):
            return self.value > other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __ge__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value >= other
        elif isinstance(other, NoteValue):
            return self.value >= other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value == other
        elif isinstance(other, NoteValue):
            return self.value == other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __ne__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return self.value != other
        elif isinstance(other, NoteValue):
            return self.value != other.value
        else:
            raise ValueError('Cannot compare NoteValue and type {0}.'.format(type(other)))

    def __add__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value + other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value + other.value)
        else:
            raise ValueError('Cannot add NoteValue and type {0}.'.format(type(other)))

    def __radd__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other + self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value + self.value)
        else:
            raise ValueError('Cannot add type {0} and NoteValue.'.format(type(other)))

    def __sub__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value - other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value - other.value)
        else:
            raise ValueError('Cannot add NoteValue and type {0}.'.format(type(other)))

    def __rsub__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other - self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value - self.value)
        else:
            raise ValueError('Cannot subtract type {0} and NoteValue.'.format(type(other)))

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value * other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value * other.value)
        else:
            raise ValueError('Cannot multiply NoteValue by type {0}.'.format(type(other)))

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other * self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value * self.value)
        else:
            raise ValueError('Cannot multiple type {0} by NoteValue.'.format(type(other)))

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value / other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value / other.value)
        else:
            raise ValueError('Cannot divide NoteValue by type {0}.'.format(type(other)))

    def __rtruediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other / self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value / self.value)
        else:
            raise ValueError('Cannot divide type {0} by NoteValue.'.format(type(other)))

    def __floordiv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value // other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value // other.value)
        else:
            raise ValueError('Cannot floor divide NoteValue by type {0}.'.format(type(other)))

    def __rfloordiv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other // self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value // self.value)
        else:
            raise ValueError('Cannot floor divide type {0} by NoteValue.'.format(type(other)))

    def __mod__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(self.value % other)
        elif isinstance(other, NoteValue):
            return NoteValue.find(self.value % other.value)
        else:
            raise ValueError('Cannot modulus NoteValue by type {0}.'.format(type(other)))

    def __rmod__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return NoteValue.find(other % self.value)
        elif isinstance(other, NoteValue):
            return NoteValue.find(other.value % self.value)
        else:
            raise ValueError('Cannot modulus type {0} by NoteValue.'.format(type(other)))
    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def max(cls, lst):
        return NoteValue.find(np.max([float(item) for item in lst]))

    @classmethod
    def min(cls, lst):
        return NoteValue.find(np.min([float(item) for item in lst]))

    @classmethod
    def sum(cls, lst):
        return NoteValue.find(np.sum([float(item) for item in lst]))

    @classmethod
    def mean(cls, lst):
        return NoteValue.find(np.mean([float(item) for item in lst]))

    @classmethod
    def std(cls, lst):
        return NoteValue.find(np.std([float(item) for item in lst]))

    @classmethod
    def exists(cls, value):
        # TODO: make all single catch
        if isinstance(value, Note):
            search = NoteValue.find(value.value)
            return search == value.value
        elif isinstance(value, NoteValue):
            search = NoteValue.find(value)
            return search == value
        elif isinstance(value, (float, np.inexact, int, np.integer)):
            search = NoteValue.find(value)
            return search == value
        else:
            print('no match', type(value))
            return False

    def from_float(self) -> 'NoteValue':
        pass

    @classmethod
    def _build_value_map(cls):
        cls._value_map_ = {}
        # for each ratio possibility
        for ratio in reversed(TupletType):
            normal, actual = ratio.normal, ratio.actual
            # for each dot possibility
            for dot in reversed(DotType):
                # for each notetype possibility
                for notetype in reversed(NoteType):
                    nt_value = (notetype.value * dot.scalar) * ratio.normal / ratio.actual
                    cls._value_map_[round(nt_value, cls._NOTEVALUE_PRECISION_)] = (notetype, dot, ratio)
        # update NoteType.None
        cls._value_map_[0] = (NoteType.NONE, DotType.NONE, TupletType.REGULAR)
        return cls._value_map_

    @classmethod
    def find(cls, value):
        def _build_value_map():
            cls._value_map_ = {}
            # for each ratio possibility
            for ratio in reversed(TupletType):
                normal, actual = ratio.normal, ratio.actual
                # for each dot possibility
                for dot in reversed(DotType):
                    # for each notetype possibility
                    for notetype in reversed(NoteType):
                        nt_value = (notetype.value * dot.scalar) * ratio.normal / ratio.actual
                        cls._value_map_[round(nt_value, cls._NOTEVALUE_PRECISION_)] = (notetype, dot, ratio)
            # update NoteType.None
            cls._value_map_[0] = (NoteType.NONE, DotType.NONE, TupletType.REGULAR)
            return cls._value_map_

        # initialize lookup table
        if not cls._value_map_:
            _build_value_map()

        if round(value, cls._NOTEVALUE_PRECISION_) in cls._value_map_:
            # exact
            note_type, dot_type, tuple_type = cls._value_map_[round(value, cls._NOTEVALUE_PRECISION_)]
            return NoteValue(note_type, dots=dot_type, ratio=Ratio(tuple_type))
        else:
            # approximate
            options_lst = list(cls._value_map_.keys())
            closest = options_lst[min(range(len(options_lst)), key=lambda i: abs(options_lst[i] - value))]
            # print('not found', value, closest, cls._value_map_[closest])
            logging.warning('NoteValue for {0} not found; approximating with {1}.'.format(value, closest))
            note_type, dot_type, tuple_type = cls._value_map_[closest]
            return NoteValue(note_type, dots=dot_type, ratio=Ratio(tuple_type))

# ----------
# Note class
# ----------
class Note:
    """
    Class to represent a note
    """

    # -----------
    # Constructor
    # -----------
    def __init__(self, value=NoteType.NONE, pitch=None):
        self.pitch = pitch
        self.value = value
        self.show_accidental = False
        self.stem = StemType.UP
        self.voice = 1
        self.attack = 0
        self.decay = 0
        self.pizzicato = False
        self.beams = []

    # ----------
    # Properties
    # ----------
    @property
    def value(self):
        return self._notevalue_.value

    @value.setter
    def value(self, value):
        # set NoteValue
        if isinstance(value, NoteValue):
            # from NoteValue
            self._notevalue_ = value
        elif isinstance(value, NoteType):
            # from NoteType
            self._notevalue_ = NoteValue(notetype=value)
        elif isinstance(value, (float, np.inexact, int, np.integer)):
            # from numeric
            self._notevalue_ = NoteValue.find(value)
        else:
            raise ValueError('Invalid type {0} for NoteValue.'.format(type(value)))

    @property
    def notevalue(self):
        return self._notevalue_.value

    @notevalue.setter
    def notevalue(self, notevalue):
        self.value = notevalue

    @property
    def midi(self):
        return self.pitch.midi

    @property
    def accidental(self):
        return self.pitch.alter

    @accidental.setter
    def accidental(self, accidental: Accidental):
        self.pitch.alter = accidental

    @property
    def glyph(self):
        # noteEmptyBlack, stem
        glyph_code = 'note'

        if self.is_beamed():
            # beamed
            if self._notevalue_ <= NoteType.HALF:
                # whole and half notes do not have beams
                glyph_code += self._notevalue_.notetype.abbr
            else:
                # unbeamed base glyph is the quarter note glyph
                glyph_code += "Quarter"
        else:
            # not beamed, use version with flag
            glyph_code += self._notevalue_.notetype.abbr

        glyph_code += self.stem.name.title()
        return glyph_code

    # --------
    # Override
    # --------
    def __str__(self):
        if self._notevalue_.ratio.is_regular():
            return str(self._notevalue_.note) + self._notevalue_.dots.symbol + ' ' + str(self.pitch)
        else:
            return str(
                self._notevalue_.ratio.actual) + '[' + self._notevalue_.note + self._notevalue_.dots.symbol + ']' + ' ' + str(
                self.pitch)

    def __repr__(self):
        return '<{self.__class__.__name__}() nt={self.notetype}, d={self.dots.value}, r={self.ratio}>'.format(
            self=self)

    def __lt__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ < other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ < other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    def __le__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ <= other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ <= other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    def __gt__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ > other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ > other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    def __ge__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ >= other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ >= other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ == other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ == other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    def __ne__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ != other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ != other
        else:
            raise TypeError('Cannot compare Note and type {0}.'.format(type(other)))

    # ---------
    # Methods
    # ---------
    def add_beam(self, beam):
        self.beams.append(beam)

    def is_beamed(self):
        return len(self.beams) > 0

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls, abc_note):
        # pitch
        print('abcnote', abc_note)

        pitch_regex = '([_^=]*[a-gA-G][\',]*)'
        note_length_regex = '([\d]*\/*)'
        regex = pitch_regex + note_length_regex
        note_match = re.match(regex, abc_note)

        if note_match:
            pitch_match = note_match.group(1)
            note_length_match = note_match.group(2)

            pitch = Pitch.from_abc(pitch_match)
            print('pitch_match', pitch_match, pitch)
            print('note_length_match', note_length_match)

        #pitch_match = re.match('.*?([_^=]*[a-gA-G][\',]*)', abc_note)
        #if pitch_match:
        #    print('npitch', pitch_match.group(1))
        #    pitch = Pitch.from_abc(pitch_match.group(1))
        #    print(pitch)
        #pass

        note_length_match = re.match('', abc_note)


    @classmethod
    def find(cls, value):
        print('note find', value)

        # look for tied values
        def find_ties(remainder):
            notetype_lst = []
            for notetype in NoteType:
                if notetype.value > remainder:
                    print('case skip')
                    continue
                elif notetype.value == remainder:
                    print('case equal', notetype.value, remainder)
                    # match exactly; last notetype to find
                    remainder -= notetype.value
                    notetype_lst.append(notetype)
                    print('case equal', notetype.value, remainder)
                    break
                else:
                    print('case subtract', notetype.value, remainder)
                    remainder -= notetype.value
                    notetype_lst.append(notetype)
                    print('case subtract', notetype.value, remainder)
            return notetype_lst, remainder

        candidate_notetype = NoteValue.find(value)
        if candidate_notetype.ratio.is_regular():
            # found with regular tuplet
            return [candidate_notetype]
        else:
            # look for tied notes
            notetype_lst, remainder = find_ties(value)
            if remainder == 0:
                # found with tied notes in 1:1
                return notetype_lst
            else:
                print('remainder', value, remainder)
                # found with single value with irregular tuplet
                return [candidate_notetype]

# ----------
# Rest class
# ----------
class Rest(Note):
    """
    Class to represent a rest
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self, value=NoteType.NONE):
        print('restconst', value)
        super().__init__(value=value)

    # ----------
    # Properties
    # ----------
    @property
    def glyph(self):
        # rest
        glyph_code = 'rest'
        print('restglyph', self._notevalue_)
        glyph_code += self._notevalue_.notetype.abbr
        return glyph_code

    # --------
    # Override
    # --------
    def __str__(self):
        if self._notevalue_.ratio.is_regular():
            return self._notevalue_.rest + self._notevalue_.dots.symbol
        else:
            return str(
                self._notevalue_.ratio.actual) + '[' + self._notevalue_.rest + self._notevalue_.dots.symbol + ']'

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------


# ---------------
# NoteGroup class
# ---------------
class NoteGroup(Note):
    # self.pitch = pitch
    # self.value = value
    # self.accidental = accidental
    # self.stem = StemType.UP
    # self.beams = []

    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.notes = []

    pass

class TiedNote(NoteGroup):
    pass

class TrilledNote(NoteGroup):
    pass

class Tuplet(NoteGroup):
    pass

class BeamGroup(NoteGroup):
    pass

class ChordType(Enum):
    MAJOR_TRIAD = 0b000010010001, ['', 'Δ'], '\U0001D148'
    MAJOR_SIXTH = 0b001010010001, ['6', 'M6', 'maj6'], '\u2076'
    DOMINANT_SEVENTH = 0b010010010001, ['7', 'dom7'], '\u2077'
    MAJOR_SEVENTH = 0b100010010001, ['M7', 'Δ7', 'maj7'], '\U0001D148\u2077'

    AUGMENTED_TRIAD = 0b000100010001, ['+', 'aug'], '\U0001D144'
    AUGMENTED_SEVENTH = 0b010100010001, ['+7', 'aug7'], '\U0001D144\u2077'

    MINOR_TRIAD = 0b000010001001, ['m', 'min'], '\u006D'
    MINOR_SIXTH = 0b001010001001, ['m6', 'min6'], '\u006D\u2076'
    MINOR_SEVENTH = 0b010010001001, ['m7', 'min7'], '\u006D\u2077'
    MINOR_MAJOR_SEVENTH = 0b100010001001, ['mM7', 'm/M7', 'm(M7)', 'minmaj7', 'min/maj7',
                                           'min(maj7)'], '\u006D\u1D39\u2077'

    DIMINISHED_TRIAD = 0b000001001001, ['°', 'o', 'dim'], '\U0001D1AC'
    DIMINISHED_SEVENTH = 0b001001001001, ['°', 'o7', 'dim7'], '\U0001D1AC\u2077'
    HALF_DIMINISHED_SEVENTH = 0b001001001001, ['ø7'], '\U0001D1A9\u2077'


class Chord(NoteGroup):
    """
    Class to represent a chord
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        pass

    # -----------
    # Constructor
    # -----------

    # ----------
    # Properties
    # ----------

    # --------
    # Override
    # --------

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
