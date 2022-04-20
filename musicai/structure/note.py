"""
Representation of a musical note or rest
"""
import re
import warnings
from enum import Enum
from typing import Union
import numpy as np

from musicai.structure.note_mark import StemType
from musicai.structure.pitch import Accidental, Pitch


# -------------
# NoteType enum
# -------------
class NoteType(Enum):
    """
    Representation the relative duration of a note or rest symbol
    """

    LARGE = (8.0, 'Large', '\U0001D1B6', '\U0001D13A')  # Alternate name: duplex longa, maxima
    LONG = (4.0, 'Long', '\U0001D1B7', '\U0001D13A')
    DOUBLE = (2.0, 'Double', '\U0001D15C', '\U0001D13B')  # Alternate name: breve
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
    def __str__(self) -> str:
        return self.name.replace("_", " ").title()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.name}) {self.value}>'

    def __float__(self) -> float:
        if isinstance(self.value, float):
            return self.value
        else:
            raise TypeError(f'{self} has a non-float type {type(self.value)} for note type length.')

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
        if not isinstance(lookup, str):
            raise TypeError(f'Cannot find NoteType to match {lookup} of type {type(lookup)}')
        string = lookup.lower().strip()
        for nt in NoteType:
            if nt.abbr.lower() == string or nt.name.lower() == string or \
                    nt.note.lower() == string or nt.rest.lower() == string:
                return nt
        raise ValueError(f'Cannot find NoteType to match {lookup} of value {type(lookup)}')

    @classmethod
    def from_float(cls, lookup: Union[float, int, np.inexact, np.integer]) -> 'NoteType':
        if not isinstance(lookup, Union[float, int, np.inexact, np.integer]):
            raise TypeError(f'Cannot find NoteType to match {lookup} of type {type(lookup)}')
        for nt in NoteType:
            if nt.value == lookup:
                return nt
        raise ValueError(f'Cannot find NoteType to match {lookup} of value {type(lookup)}')

    @classmethod
    def from_mxml(cls, mxml_notetype: str) -> 'NoteType':
        if mxml_notetype.upper() in [n.name for n in NoteType]:
            return NoteType[mxml_notetype.upper()]

        match mxml_notetype.lower():
            # allowed mxml values
            case '1024th':
                return NoteType.ONE_THOUSAND_TWENTY_FOURTH
            case '512th':
                return NoteType.FIVE_HUNDRED_TWELFTH
            case '256th':
                return NoteType.TWO_FIFTY_SIXTH
            case '128th':
                return NoteType.ONE_TWENTY_EIGHTH
            case '64th':
                return NoteType.SIXTY_FOURTH
            case '32nd':
                return NoteType.THIRTY_SECOND
            case '16th':
                return NoteType.SIXTEENTH
            case 'breve':
                return NoteType.DOUBLE
            case 'maxima':
                return NoteType.LARGE

            # unallowed mxml values
            case '2048th':
                return NoteType.TWO_THOUSAND_FORTY_EIGHTH
            case '4096th':
                return NoteType.FOUR_THOUSAND_NINETY_SIXTH
            case _:
                warnings.warn(f'MXL Notetype "{mxml_notetype.title()}" not supported--returning Notetype.QUARTER')
                return NoteType.QUARTER

    # @classmethod
    # def find(cls, lookup: Union[str, float]) -> 'NoteType':
    #     if isinstance(lookup, float):
    #         for nt in NoteType:
    #             if nt.value == lookup:
    #                 return nt
    #     elif isinstance(lookup, str):
    #         string = lookup.lower().strip()
    #         for nt in NoteType:
    #             if nt.abbr.lower() == string or nt.name.lower() == string or \
    #                                   nt.note.lower() == string or nt.rest.lower() == string:
    #                 return nt
    #     raise ValueError(f'Cannot find NoteType to match {lookup} of type {type(lookup)}')


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
    def __str__(self) -> str:
        return self.name.title()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.name}) {self.scalar}>'

    def __mul__(self, other: Union[float, int, np.inexact, np.integer, 'DotType']) -> Union[float, int]:
        if isinstance(other, DotType):
            return self.scalar * other.scalar
        elif isinstance(other, Union[float, int, np.inexact, np.integer]):
            return self.scalar * other
        else:
            raise TypeError(f'Cannot multiply DotValue and type {type(other)}.')

    def __rmul__(self, other: Union[float, int, np.inexact, np.integer, 'DotType']) -> Union[float, int]:
        if isinstance(other, DotType):
            return other.scalar * self.scalar
        elif isinstance(other, Union[float, int, np.inexact, np.integer]):
            return other * self.scalar
        else:
            raise TypeError(f'Cannot multiply type {type(other)} and DotValue.')

    def __truediv__(self, other: Union[float, int, np.inexact, np.integer, 'DotType']) -> Union[float, int]:
        if isinstance(other, DotType):
            return self.scalar / other.scalar
        elif isinstance(other, Union[float, int, np.inexact, np.integer]):
            return self.scalar / other
        else:
            raise TypeError(f'Cannot divide DotValue and type {type(other)}.')

    def __rtruediv__(self, other: Union[float, int, np.inexact, np.integer, 'DotType']) -> Union[float, int]:
        if isinstance(other, DotType):
            return other.scalar / self.scalar
        elif isinstance(other, Union[float, int, np.inexact, np.integer]):
            return other / self.scalar
        else:
            raise TypeError(f'Cannot divide type {type(other)} and DotValue.')

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
    # n (actual) notes over the time of m (normal)
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
        return f'<{self.__class__.__name__}({self.name}) {self.symbol}>'

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
    Class to represent a ratio, either custom or from a tuplettype
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self, ratio: Union['Ratio', TupletType, tuple] = None):
        self._tuplettype_ = None
        self.custom = False  # if True, ignore TupletType
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
            raise TypeError(f'Cannot create Tuplet from type {type(ratio)}.')

    # ----------
    # Properties
    # ----------
    @property
    def actual(self) -> int:
        return self._actual_

    @actual.setter
    def actual(self, actual):
        self._actual_ = actual
        self._update_tuplettype_()

    @property
    def normal(self) -> int:
        return self._normal_

    @normal.setter
    def normal(self, normal: int):
        self._normal_ = normal
        self._update_tuplettype_()

    @property
    def tuplettype(self) -> TupletType:
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
    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.symbol})>'

    # ---------
    # Methods
    # ---------
    def _update_tuplettype_(self):
        self.symbol = str(self.actual) + ':' + str(self.normal)
        if (self._actual_, self._normal_) not in TupletType._value2member_map_:
            # custom ratio
            self._tuplettype_ = None
            self.custom = True
        else:
            # find tuplettype
            self._tuplettype_ = TupletType((self._actual_, self._normal_))
            self.custom = False

    def is_regular(self) -> bool:
        if self._tuplettype_ is None:
            return self._actual_ == 1 and self._normal_ == 1
        return self._tuplettype_ is TupletType.REGULAR


# ---------------
# Notevalue class
# ---------------
class NoteValue:
    """
    Class to represent the relative duration of a note or rest, taking into account augmentation and tuplets
    """
    _value_map_ = {}
    _NOTEVALUE_PRECISION_ = 20

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 notetype: Union[int, np.inexact, float, np. integer, NoteType] = NoteType.QUARTER,
                 dots: Union['DotType', int, np.integer] = DotType.NONE,
                 ratio: Union['Ratio', TupletType, tuple] = Ratio(TupletType.REGULAR)):
        self.notetype = notetype, False  # False--do not force a notevalue update
        self.dots = dots, False  # False--do not force a notevalue update
        self.ratio = Ratio(ratio)
        self._value_ = self.notetype.value * self.dots * self.ratio.normal / self.ratio.actual

    # ----------
    # Properties
    # ----------
    @property
    def notetype(self) -> NoteType:
        return self._notetype_

    @notetype.setter
    def notetype(self, value: Union[int, np.inexact, float, np. integer, NoteType, tuple]):

        # To NOT force a notevalue update, a tuple with type bool as the second tuple item can be passed in
        if isinstance(value, tuple):
            if not isinstance(value[1], bool):
                raise TypeError(f'Any tuple passed into notetype must have a the second tuple item be of type bool. '
                                f'Cannot accept type {type(value[1])}.')
            force_value_update = value[1]
            value = value[0]
        else:
            force_value_update = True

        if isinstance(value, Union[int, np.integer, float, np.inexact]):
            if value in NoteType._value2member_map_:
                self._notetype_ = NoteType(value)
            else:
                warnings.warn(f'No valid NoteType for {value}, setting NoteValue NoteType to NoteType.QUARTER',
                              stacklevel=2)
                self._notetype_ = NoteType.QUARTER
        elif isinstance(value, NoteType):
            self._notetype_ = value
        else:
            raise TypeError(f'Cannot find a NoteValue NoteType from type {type(value)}')

        if force_value_update:
            self.update_notevalue()

    @property
    def dots(self) -> DotType:
        return self._dots_

    @dots.setter
    def dots(self, value: Union[int, np.integer, DotType, tuple]):

        # To NOT force a notevalue update, a tuple with type bool as the second tuple item can be passed in
        if isinstance(value, tuple):
            if not isinstance(value[1], bool):
                raise TypeError(f'Any tuple passed into notetype must have a the second tuple item be of type bool. '
                                f'Cannot accept type {type(value[1])}.')
            force_value_update = value[1]
            value = value[0]
        else:
            force_value_update = True

        if isinstance(value, Union[int, np.integer]):
            assert -1 < value < 5, 'Only an amount of 0-4 dots are supported'
            self._dots_ = DotType(value)
        elif isinstance(value, DotType):
            self._dots_ = value
        else:
            raise TypeError(f'Cannot find a NoteValue DotType from type {type(value)}')

        if force_value_update:
            self.update_notevalue()

    @property
    def value(self) -> float:
        if self.ratio is None:
            return self.notetype.value * self.dots
        else:
            return (self.notetype.value * self.dots) * self.ratio.normal / self.ratio.actual

    @value.setter
    def value(self, value: Union[float, int, np.integer, np.inexact]):
        new_note_value = NoteValue.find(value)

        self.notetype = new_note_value.notetype
        self.dots = new_note_value.dots
        self.ratio = new_note_value.ratio
        self._value_ = new_note_value.value

    @property
    def note(self):
        return self.notetype.note

    @property
    def rest(self):
        return self.notetype.rest

    # --------
    # Override
    # --------
    def __float__(self) -> float:
        return self.value

    def __int__(self) -> int:
        return round(self.value)

    def __str__(self) -> str:
        return f'{self.value}'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.value}) nt={self.notetype}, d={self.dots.value}, r={self.ratio}>'

    def __lt__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value < other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value < other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __le__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value <= other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value <= other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __gt__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value > other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value > other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __ge__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value >= other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value >= other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __eq__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value == other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value == other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __ne__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> bool:
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return self.value != other
        elif isinstance(other, Union[NoteValue, NoteType]):
            return self.value != other.value
        else:
            raise TypeError(f'Cannot compare NoteValue and type {type(other)}.')

    def __add__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value + other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value + other.value)
        else:
            raise TypeError(f'Cannot add NoteValue and type {type(other)}.')

    def __radd__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other + self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value + self.value)
        else:
            raise TypeError(f'Cannot add type {type(other)} and NoteValue.')

    def __sub__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union['NoteValue', int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value - other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value - other.value)
        else:
            raise TypeError(f'Cannot subtract NoteValue and type {type(other)}.')

    def __rsub__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other - self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value - self.value)
        else:
            raise TypeError(f'Cannot subtract type {type(other)} and NoteValue.')

    def __mul__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value * other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value * other.value)
        else:
            raise TypeError(f'Cannot multiply NoteValue and type {type(other)}.')

    def __rmul__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other * self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value * self.value)
        else:
            raise TypeError(f'Cannot multiply type {type(other)} by NoteValue.')

    def __truediv__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value / other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value / other.value)
        else:
            raise TypeError(f'Cannot divide NoteValue by type {type(other)}.')

    def __rtruediv__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other / self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value / self.value)
        else:
            raise TypeError(f'Cannot divide type {type(other)} by NoteValue.')

    def __floordiv__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value // other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value // other.value)
        else:
            raise TypeError(f'Cannot floor divide NoteValue by type {type(other)}.')

    def __rfloordiv__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other // self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value // self.value)
        else:
            raise TypeError(f'Cannot floor divide type {type(other)} by NoteValue.')

    def __mod__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(self.value % other)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(self.value % other.value)
        else:
            raise TypeError(f'Cannot modulus NoteValue by type {type(other)}.')

    def __rmod__(self, other: Union['NoteValue', 'NoteType', int, float, np.inexact, np.integer]) -> 'NoteValue':
        if isinstance(other, Union[int, float, np.inexact, np.integer]):
            return NoteValue.find(other % self.value)
        elif isinstance(other, Union[NoteValue, NoteType]):
            return NoteValue.find(other.value % self.value)
        else:
            raise TypeError(f'Cannot modulus type {type(other)} by NoteValue.')

    # ---------
    # Methods
    # ---------
    def update_notevalue(self):
        self._value_ = self.notetype.value * self.dots * self.ratio.normal / self.ratio.actual

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def max(cls, lst: list) -> 'NoteValue':
        return NoteValue.find(np.max([float(item) for item in lst]))

    @classmethod
    def min(cls, lst: list) -> 'NoteValue':
        return NoteValue.find(np.min([float(item) for item in lst]))

    @classmethod
    def sum(cls, lst: list) -> 'NoteValue':
        return NoteValue.find(float(np.sum([float(item) for item in lst])))

    @classmethod
    def mean(cls, lst: list) -> 'NoteValue':
        return NoteValue.find(float(np.mean([float(item) for item in lst])))

    @classmethod
    def std(cls, lst: list) -> 'NoteValue':
        return NoteValue.find(float(np.std([float(item) for item in lst])))

    @classmethod
    def exists(cls, value: Union['Note', float, int, np.inexact, np.integer]) -> bool:
        # TODO: make all single catch
        if isinstance(value, Note):
            search = NoteValue.find(value.value)
            return search == value.value
        elif isinstance(value, (float, np.inexact, int, np.integer)):
            search = NoteValue.find(value)
            return search == value
        else:
            print('No match', type(value))
            return False

    @classmethod
    def find(cls, value: Union[float, int, np.integer, np.inexact]) -> 'NoteValue':
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
            # return cls._value_map_

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
            warnings.warn(f'NoteValue for {value} not found; approximating with {closest}.', stacklevel=2)
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
    def __init__(self,
                 value: NoteValue = NoteValue(NoteType.NONE),
                 pitch: Pitch = Pitch(),
                 marks: set = None):
        self.value = value
        self.pitch = pitch
        if marks is None:
            marks = set()  # This is done because set is a mutable type
        self.marks = marks

        self.location = 0
        self.division = 256

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
    def value(self) -> NoteValue:
        return self._notevalue_

    @value.setter
    def value(self, value: Union['NoteValue', 'NoteType', float, int, np.integer, np.inexact]):
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
            raise TypeError(f'Invalid type {type(value)} for NoteValue.')

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
                self._notevalue_.ratio.actual) + '[' + self._notevalue_.note + self._notevalue_.dots.symbol + ']' \
                   + ' ' + str(self.pitch)

    def __repr__(self):
        return f'<{self.__class__.__name__}() nt={self.value.notetype}, d={self.value.dots}, r={self.value.ratio}>'

    def __lt__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ < other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ < other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    def __le__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ <= other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ <= other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    def __gt__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ > other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ > other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    def __ge__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ >= other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ >= other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    def __eq__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ == other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ == other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    def __ne__(self, other):
        if isinstance(other, Note):
            return self._notevalue_ != other._notevalue_
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self._notevalue_ != other
        else:
            raise TypeError(f'Cannot compare Note and type {type(other)}.')

    # ---------
    # Methods
    # ---------
    # def contains_start_tie(self) -> bool:
        # return (x in note_marks where x is a note mark of type tie)

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

        # pitch_match = re.match('.*?([_^=]*[a-gA-G][\',]*)', abc_note)
        # if pitch_match:
        #    print('npitch', pitch_match.group(1))
        #    pitch = Pitch.from_abc(pitch_match.group(1))
        #    print(pitch)
        # pass

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
    def __init__(self, value: NoteType = NoteType.NONE):
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
    @classmethod
    def to_rest(cls, origin_note: Note) -> 'Rest':
        new_rest = Rest()

        for attr in vars(origin_note).items():  # for every item in the original note
            vars(new_rest).update({attr[0]: attr[1]})  # update this item in the rest

        new_rest.pitch = None
        return new_rest


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
