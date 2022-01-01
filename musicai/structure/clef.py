from enum import Enum

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
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)


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
        return '<{self.__class__.__name__}({self.abbr})>'.format(self=self)

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
    def __init__(self, clef=ClefType.G, octave=ClefOctave.NORMAL, line=2):
        # ClefType (default G)
        if isinstance(clef, ClefType):
            self.cleftype = clef
        elif isinstance(clef, str):
            # accepts G, F, C, PERCUSSION, TAB
            self.cleftype = ClefType[clef.upper()]
        else:
            raise TypeError('Cannot create ClefType from {0} of type {1}.'.format(clef, type(clef)))

        # ClefOctave (default 2)
        if isinstance(octave, ClefOctave):
            self.octave_change = octave
        elif isinstance(octave, (int, np.integer)):
            self.octave_change = ClefOctave(octave)
        else:
            raise TypeError('Cannot create ClefOctave from {0} of type {1}.'.format(octave, type(octave)))

        if isinstance(line, (str, int, np.integer)):
            self.line = int(line)
        else:
            raise TypeError('Cannot create Clef line from {0} of type {1}.'.format(line, type(line)))

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
        return '<{self.__class__.__name__}({self.cleftype}{self.octave_change})>'.format(self=self)

    def __lt__(self, other):
        if isinstance(other, Clef):
            return self.value < other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value < other
        else:
            raise TypeError('Cannot compare Clef and {0} of type {1}.'.format(other, type(other)))

    def __le__(self, other):
        if isinstance(other, Clef):
            return self.value <= other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value <= other
        else:
            raise TypeError('Cannot compare Clef and {0} of type {1}.'.format(other, type(other)))

    def __eq__(self, other):
        if isinstance(other, Clef):
            return self.value == other.value
        elif isinstance(other, (int, np.integer, float, np.inexact)):
            return self.value == other
        else:
            raise TypeError('Cannot compare Clef and {0} of type {1}.'.format(other, type(other)))

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------