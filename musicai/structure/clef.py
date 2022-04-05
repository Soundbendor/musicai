from enum import Enum
from typing import Union

import numpy as np


# -------------
# ClefType enum
# -------------
class ClefType(Enum):
    """
    Enum to represent the type of the clef
    """
    NONE = 0, 0, ''
    F = 1, 53, 'fClef'
    C = 2, 60, 'cClef'
    G = 3, 67, 'gClef'
    PERCUSSION = 4, 0, 'unpitchedPercussionClef1'
    SEMIPITCHED = 5, 0, 'semipitchedPercussionClef1'
    TAB4 = 6, 0, '4stringTabClef'
    TAB6 = 7, 0, '6stringTabClef'
    #JIANPU = 8, 0, ''

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.midi = values[1]
        obj.glyph = values[2]
        return obj

    # --------
    # Override
    # --------
    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.name})>'

    # --------
    # Class Methods
    # --------
    @classmethod
    def from_str(cls, value: str) -> 'ClefType':
        match value.lower():
            case 'g': return ClefType.G
            case 'f': return ClefType.F
            case 'c': return ClefType.C
            case 'percussion': return ClefType.PERCUSSION
            case 'tab': return ClefType.TAB6
            # case 'jianpu': return ClefType.JIANPU
            case 'none': return ClefType.G  # returns treble for musicxml loading
            case _: return ClefType.NONE


# ---------------
# ClefOctave enum
# ---------------
class ClefOctave(Enum):
    """
    Enum to represent the octave adjustment
    """
    VENTIDUESIMA_BASSA = -3, '22mb', '22ma bassa', '22m bassa', 'ventiduesima bassa'
    QUINDICESIMA_BASSA = -2, '15mb', '15ma bassa', '15m bassa', 'quindicesima bassa'
    OTTAVA_BASSA = -1, '8vb', '8va bassa', '8v bassa', 'ottava bassa'
    NORMAL = 0, '', '', '', ''
    OTTAVA_ALTA = 1, '8va', '8va alta', '8v alta', 'ottava alta'
    QUINDICESIMA_ALTA = 2, '15ma', '15ma alta', '15m alta', 'quindicesima alta'
    VENTIDUESIMA_ALTA = 3, '22ma', '22ma alta', '22m alta', 'ventiduesima alta'

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.abbr = values[1]
        obj.short_name = values[2]
        obj.alternate_name = values[3]
        obj.long_name = values[4]
        return obj

    # ----------
    # Properties
    # ----------
    @property
    def glyph(self):
        return self.abbr

    # --------
    # Override
    # --------
    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.abbr})>'

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value


# ----------
# Clef class
# ----------
class Clef:
    """
    Class to represent a musical clef
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 clef: Union[ClefType, str] = ClefType.G,
                 octave: Union[int, np.integer, ClefOctave] = ClefOctave.NORMAL,
                 line: Union[str, int, np.integer] = 2):
        # ClefType (default G)
        if isinstance(clef, ClefType):
            self.cleftype = clef
        elif isinstance(clef, str):
            self.cleftype = ClefType.from_str(clef)
        else:
            raise TypeError(f'Cannot create ClefType from {clef} of type {type(clef)}.')

        # ClefOctave (default 2)
        if isinstance(octave, ClefOctave):
            self.octave_change = octave
        elif isinstance(octave, (int, np.integer)):
            assert -4 < octave < 4
            self.octave_change = ClefOctave(octave)
        else:
            raise TypeError(f'Cannot create ClefOctave from {octave} of type {type(octave)}.')

        if isinstance(line, (str, int, np.integer)):
            self.line = int(line)
        else:
            raise TypeError(f'Cannot create Clef line from {line} of type {type(line)}.')

    # ----------
    # Properties
    # ----------
    @property
    def value(self):
        value = self.cleftype.midi
        value += 12 * self.octave_change
        return value

    @property
    def glyph(self):
        return self.cleftype.glyph + self.octave_change.glyph

    # --------
    # Override
    # --------
    def __int__(self):
        return int(self.value)

    def __str__(self):
        return str(self.cleftype + self.octave_change)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.cleftype}{self.octave_change})>'

    def __lt__(self, other):
        if isinstance(other, Clef):
            return self.value < other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value < other
        else:
            raise TypeError(f'Cannot compare Clef and {other} of type {type(other)}.')

    def __le__(self, other):
        if isinstance(other, Clef):
            return self.value <= other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value <= other
        else:
            raise TypeError(f'Cannot compare Clef and {other} of type {type(other)}.')

    def __eq__(self, other):
        if isinstance(other, Clef):
            return self.value == other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value == other
        else:
            raise TypeError(f'Cannot compare Clef and {other} of type {type(other)}.')

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------