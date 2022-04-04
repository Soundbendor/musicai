import logging
import warnings
import re
from enum import Enum
from typing import Union, Tuple
import numpy as np

from musicai.structure.clef import Clef


# ---------
# Step enum
# ---------
class Step(Enum):
    """
    Enum to represent whole tone steps
    """
    C = 0, 0, 'red'
    D = 2, 1, 'orange'
    E = 4, 2, 'yellow'
    F = 5, 3, 'green'
    G = 7, 4, 'blue'
    A = 9, 5, 'indigo'
    B = 11, 6, 'purple'

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.whole = values[1]
        obj.color = values[2]
        obj._all_values = values
        return obj

    # --------
    # Override
    # --------
    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)

    def __add__(self, other: Union['Step', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Step):
            return self.value + other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value + other
        else:
            raise TypeError('Cannot add Step and type {0}.'.format(type(other)))

    def __sub__(self, other: Union['Step', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Step):
            return self.value - other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value - other
        else:
            raise TypeError('Cannot subtract Step and type {0}.'.format(type(other)))

    def __mod__(self, other: Union['Step', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Step):
            return self.value % other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value % other
        raise TypeError('Cannot modulate Step and type {0}.'.format(type(other)))

    # ---------
    # Methods
    # ---------
    def next(self) -> 'Step':
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            index = 0
        return members[index]

    def prev(self) -> 'Step':
        cls = self.__class__
        members = list(cls)
        index = members.index(self) - 1
        if index < 0:
            index = len(members) - 1
        return members[index]

    def diff(self, other: 'Step') -> int:
        if isinstance(other, Step):
            if other == self:
                # same step
                return 0

            count = 0
            cur_step = self
            if self.value < other.value:
                while cur_step != other:
                    cur_step = cur_step.next()
                    count += 1
            else:
                while cur_step != other:
                    cur_step = cur_step.prev()
                    count -= 1

            return count
        else:
            raise TypeError('Cannot find difference between Step and type {0}.'.format(type(other)))

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def has_name(cls, name: str) -> bool:
        return name in cls._member_names_

    @classmethod
    def has_value(cls, value: int) -> bool:
        return value % 12 in cls._value2member_map_

    # @classmethod
    # def from_color(cls, color_step: Color) -> 'Step':
    # for name, offset in Accidental.__members__.items():

    @classmethod
    def from_int(cls, int_step: int) -> Union['Step', 'Chromatic']:
        pass

    @classmethod
    def from_str(cls, str_step: str) -> 'Step':
        value = str_step.strip()
        if re.match('^[A-G]$', value.upper()):
            return Step[str(value).upper()]
        else:
            # Byzantium: Pa, Vu, Ga, Di, Ke, Zo, Ni
            # Solfège: do (doh), re, mi, fa, so(l), la, and ti (si)
            # German: H = B-natural
            value = value.lower()
            value = value.replace('ut', 'C').replace('do', 'C').replace('doh', 'C').replace('pa', 'C')
            value = value.replace('re', 'D').replace('vu', 'D')
            value = value.replace('me', 'E').replace('ga', 'E')
            value = value.replace('fa', 'F').replace('di', 'F')
            value = value.replace('so', 'G').replace('sol', 'G').replace('ke', 'G')
            value = value.replace('la', 'A').replace('zo', 'A')
            value = value.replace('si', 'B').replace('ti', 'B').replace('h', 'B').replace('ni', 'B')

            if Step.has_name(value):
                return Step[value]

            # TODO: open question, should we accept and ignore accidentals, e.g. C♭ -> C ?

            raise ValueError('Cannot convert string {0} to Step'.format(str_step))


# -----------
# Octave enum
# -----------
class Octave(Enum):
    """
    Enum to represent a musical octave
    """
    # Scientific octave, pedal, octave subscript, MIDI note number,
    # MIDI range min, MIDI range max, frequency range min, frequency range max
    NONE = (-2, None, None, None, None)
    SUB_SUB_CONTRA = (-1, '64 Foot', -5, 0, 11, 16.35, 30.87)
    SUB_CONTRA = (0, '32 Foot', -4, 12, 23, 32.70, 61.74)
    CONTRA = (1, '16 Foot', -3, 24, 35, 27.5, 65.41, 123.47)
    GREAT = (2, '8 Foot', -2, 36, 47, 130.81, 246.94)
    SMALL = (3, '4 Foot', -1, 48, 59, 261.63, 493.88)
    ONE_LINE = (4, '2 Foot', 0, 60, 71, 523.25, 987.77)
    TWO_LINE = (5, '1 Foot', 1, 72, 83, 1046.50, 1975.53)
    THREE_LINE = (6, '3 Line', 2, 84, 95, 2093.00, 3951.07)
    FOUR_LINE = (7, '4 Line', 3, 96, 107, 4186.01, 7902.13)
    FIVE_LINE = (8, '64 Foot', 4, 108, 119, 8372.02, 15804.27)
    SIX_LINE = (9, '6 Line', 5, 120, 131, 16744.04, 31608.53)
    SEVEN_LINE = (10, '7 Line', 6, 132, 143, 33488.07, 63217.06)

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.organ_name = values[1]
        obj.midi_name = values[2]
        obj.midi_low = values[3]
        obj.midi_high = values[4]
        obj._all_values = values
        return obj

    # --------
    # Override
    # --------
    def __int__(self):
        return self._value_

    def __str__(self):
        return '' if self.value is None else str(self.value)

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)

    def __add__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return self.value + other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value + other
        else:
            raise TypeError('Cannot add Octave and type {0}.'.format(type(other)))

    def __radd__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return other.value + self.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other + self.value
        else:
            raise TypeError('Cannot add Octave and type {0}.'.format(type(other)))

    def __sub__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return self.value - other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value - other
        else:
            raise TypeError('Cannot subtract Octave and type {0}.'.format(type(other)))

    def __rsub__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return other.value - self.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other - self.value
        else:
            raise TypeError('Cannot subtract Octave and type {0}.'.format(type(other)))

    def __mul__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return self.value * other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value * other
        else:
            raise TypeError('Cannot multiply Octave and type {0}.'.format(type(other)))

    def __rmul__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return other.value * self.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other * self.value
        else:
            raise TypeError('Cannot multiply Octave and type {0}.'.format(type(other)))

    def __truediv__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return self.value / other.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.value / other
        else:
            raise TypeError('Cannot divide Octave and type {0}.'.format(type(other)))

    def __rtruediv__(self, other: Union['Octave', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Octave):
            return other.value / self.value
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other / self.value
        else:
            raise TypeError('Cannot divide Octave and type {0}.'.format(type(other)))

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    # @classmethod
    # def __missing__(cls, value):
    #     Octave.find(value)

    @classmethod
    def from_int(cls, value: int) -> 'Octave':
        if value in cls._value2member_map_:
            return Octave(value)
        else:
            raise ValueError('{0} is not a valid value for Octave.'.format(value))


    # @classmethod
    # def find(cls, value):
    #    for name, value in Octave.__members__.items():
    #        if int(value) == int(value):
    #            return Octave[name]
    #    raise ValueError('Error: octave {0} not found.'.format(value))


# ---------------
# Accidental enum
# ---------------
class Accidental(Enum):
    """
    Enum to represent a musical accidental
    """

    TRIPLE_FLAT = (-3.0, 'bbb', '♭𝄫', 'accidentalTripleFlat')
    DOUBLE_FLAT = (-2.0, 'db', '𝄫', 'accidentalDoubleFlat')
    FLAT_FLAT = (-2.0, 'bb', '♭♭', 'accidentalDoubleFlat')
    FLAT = (-1.0, 'b', '♭', 'accidentalFlat')
    NATURAL_FLAT = (-1.0, 'nb', '♮♭', 'accidentalNaturalFlat')
    THREE_QUARTERS_FLAT = (-0.75, '3qb', '𝄳♭', 'accidentalThreeQuarterTonesFlatArrowDown   ')
    QUARTER_FLAT = (-0.25, 'qb', '𝄳', 'accidentalQuarterToneFlatArrowUp')
    NONE = (0.0, '', '', '')
    NATURAL = (0.0, 'n', '♮', 'accidentalNatural')
    # NATURAL_NATURAL = (0.0, 'nn', '♮♮', 'accidentalNatural')  # incorrect glyph
    QUARTER_SHARP = (0.25, 'qs', '𝄲', 'accidentalQuarterToneSharpArrowDown')
    THREE_QUARTERS_SHARP = (0.75, '3qs', '𝄲♯', 'accidentalThreeQuarterTonesSharpArrowUp')
    SHARP = (1.0, 's', '♯', 'accidentalSharp')
    NATURAL_SHARP = (1.0, 'ns', '♮♯', 'accidentalNaturalSharp')
    DOUBLE_SHARP = (2.0, 'ds', '𝄪', 'accidentalDoubleSharp')
    SHARP_SHARP = (2.0, 'ss', '♯♯', 'accidentalSharpSharp')
    TRIPLE_SHARP = (3.0, 'sss', '♯𝄪', 'accidentalTripleSharp')

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[1]  # abbr, TODO may need to change
        obj.alter = values[0]
        obj.abbr = values[1]
        obj.symbol = values[2]
        obj.glyph = values[3]
        obj._all_values = values
        return obj

    # ----------
    # Properties
    # ----------
    @property
    def value(self):
        return self.alter

    # --------
    # Override
    # --------
    def __float__(self):
        return self.alter

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)

    def __add__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return self.alter + other.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.alter + other
        else:
            raise TypeError('Cannot add Accidental and type {0}.'.format(type(other)))

    def __radd__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return other.alter + self.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other + self.alter
        else:
            raise TypeError('Cannot add type {0} and Accidental.'.format(type(other)))

    def __sub__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return self.alter - other.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.alter - other
        else:
            raise TypeError('Cannot subtract Accidental and type {0}.'.format(type(other)))

    def __rsub__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return other.alter - self.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other - self.alter
        else:
            raise TypeError('Cannot subtract Accidental and type {0}.'.format(type(other)))

    def __mul__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return self.alter * other.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.alter * other
        else:
            raise TypeError('Cannot multiply Accidental and type {0}.'.format(type(other)))

    def __rmul__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return other.alter * self.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other * self.alter
        else:
            raise TypeError('Cannot multiply Accidental and type {0}.'.format(type(other)))

    def __truediv__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return self.alter / other.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.alter / other
        else:
            raise TypeError('Cannot divide Accidental and type {0}.'.format(type(other)))

    def __rtruediv__(self, other: Union['Accidental', float, int, np.inexact, np.integer]) -> Union[float, int]:
        if isinstance(other, Accidental):
            return other.alter / self.alter
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other / self.alter
        else:
            raise TypeError('Cannot divide Accidental and type {0}.'.format(type(other)))

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def find(cls, value: Union[str, int, float]) -> 'Accidental':
        if isinstance(value, str):
            # from string
            for name, offset in Accidental.__members__.items():
                if Accidental[name].abbr == value:
                    return Accidental[name]
        elif isinstance(value, (int, float, np.number)):
            # from numeric
            for name, offset in Accidental.__members__.items():
                if float(offset) == float(value):
                    return Accidental[name]
        raise ValueError('Error: accidental {0} not found.'.format(value))

    @classmethod
    def from_mxml(cls, mxml_accidental: str) -> 'Accidental':
        if mxml_accidental.upper().replace('-', '_') in [a.name for a in Accidental]:
            return Accidental[mxml_accidental.upper().replace('-', '_')]
        else:
            warnings.warn(f'No implementation for accidental "{mxml_accidental}" yet--returning Accidental.NONE')
            return Accidental.NONE

    @classmethod
    def from_abc(cls, abc_accidental: str) -> 'Accidental':
        str_accidental = abc_accidental.strip()
        match str_accidental:
            case '':
                return Accidental.NONE
            case '^':
                return Accidental.SHARP
            case '_':
                return Accidental.FLAT
            case '=':
                return Accidental.NATURAL
            case '^^':
                return Accidental.DOUBLE_SHARP
            case '__':
                return Accidental.DOUBLE_FLAT
            case '=^':
                return Accidental.NATURAL_SHARP
            case '=_':
                return Accidental.NATURAL_FLAT
            case '^^^':
                return Accidental.TRIPLE_SHARP
            case '___':
                return Accidental.TRIPLE_FLAT
            case _:
                raise ValueError('Error: abc accidental {0} not found.'.format(abc_accidental))


# -----------
# Pitch class
# -----------
class Pitch:
    """
    Class to represent a musical pitch
    """

    # -----------
    # Constructor
    # -----------
    def __init__(
            self,
            step: Union['Step', str, int, np.integer] = Step.C,
            octave: 'Octave' = Octave.ONE_LINE,
            alter: 'Accidental' = Accidental.NONE):

        if isinstance(step, Step):
            self.step = step
        # elif isinstance(step, (int, np.integer)): # from_int() and from_str() are not completed yet
        #    self.step = Step.from_int(step)
        # elif isinstance(step, str):
        #    self.step = Step.from_str(step)
        else:
            raise TypeError('Error: Pitch cannot be made from a step of type {0}.'.format(type(step)))

        self.octave = octave
        self.alter = alter

    # def __init__(self, pitch: Union[Step, str, float, int, np.inexact, np.integer, Tuple[Step, Octave]] = 'C4',
    #              alter: Accidental = Accidental.NONE):
    #     self.alter = alter
    #     if isinstance(pitch, Step):
    #         # from Step
    #         self.step = pitch
    #         self.octave = Octave.NONE
    #     elif isinstance(pitch, Pitch):
    #         # from Pitch
    #         self.step = pitch.step
    #         self.octave = pitch.octave
    #         self.alter = pitch.alter
    #     elif isinstance(pitch, str):
    #         # from string
    #         pitch = pitch.lower()
    #         pitch = pitch.replace('♭', 'b').replace('-flat', 'b')
    #         pitch = pitch.replace('♯', 's').replace('#', 's').replace('-sharp', 's')
    #         pitch = pitch.replace('♮', 'n').replace('-nat', 'n').replace('-natural', 'n')
    #         pitch = pitch.replace('h', 'b')  # German H=B, B=Bb (unhandled)
    #         pitch = pitch.replace('ut', 'c').replace('do', 'c').replace('re', 'd').replace('me', 'e') \
    #             .replace('fa', 'f').replace('sol', 'g').replace('la', 'a').replace('si', 'b')
    #
    #         step_letter = pitch[0].upper()
    #         pitch = pitch[1:]  # pop first char
    #         if Step.has_name(step_letter):
    #             self.step = Step[step_letter]
    #         else:
    #             raise ValueError('Cannot find Pitch step for {0}'.format(step_letter))
    #
    #         # accidental (optional)
    #         split_lst = re.split('(-?\d+)', pitch)
    #         accidental_letter = split_lst[0]
    #         pitch = split_lst[1]
    #         if accidental_letter:
    #             self.alter = Accidental.find(accidental_letter.lower())
    #
    #         # octave
    #         if (pitch.strip('-')).isnumeric():
    #             octave_number = int(pitch)
    #             self.octave = Octave(octave_number)
    #         else:
    #             raise ValueError('Cannot find Pitch octave for {0}'.format(pitch))
    #     elif isinstance(pitch, (float, np.inexact, int, np.integer)):
    #         # from numeric (midi)
    #         pitch = int(pitch)
    #         if Step.has_value(pitch % 12):
    #             self.step = Step(pitch % 12)
    #         else:
    #             self.step = Step(pitch % 12 + 1)
    #         self.octave = Octave(pitch // 12 - 1)
    #     elif isinstance(pitch, tuple):
    #         # from (Step, Octave) tuple
    #         if isinstance(pitch[0], Step) and isinstance(pitch[0], (Octave, int, np.integer)):
    #             self.step = pitch[0]
    #             self.octave = Octave(int(pitch[1]))
    #         else:
    #             raise ValueError('Cannot find Pitch for {0}'.format(pitch))
    #     else:
    #         raise ValueError('Cannot find Pitch for {0}'.format(pitch))

    # ----------
    # Properties
    # ----------
    @property
    def midi(self) -> int:
        return round(self.step + 12 * (self.octave + 1) + self.alter)

    @midi.setter
    def midi(self, value):
        logging.warning(f'Setting midi not implemented yet for Pitch in {str(self)}')

    @property
    def unaltered(self) -> int:
        # midi value but not including accidental
        return round(self.step + 12 * (self.octave + 1))

    # --------
    # Override
    # --------
    def __str__(self):
        return str(self.step) + str(self.alter) + str(self.octave)

    def __repr__(self):
        return f'<{self.__class__.__name__}({str(self.step)})>'

    def __lt__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi < other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi < other
        elif isinstance(other, Clef):
            return self.midi < other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __le__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi <= other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi <= other
        elif isinstance(other, Clef):
            return self.midi <= other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __gt__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi > other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi > other
        elif isinstance(other, Clef):
            return self.midi > other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __ge__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi >= other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi >= other
        elif isinstance(other, Clef):
            return self.midi >= other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __eq__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi == other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi == other
        elif isinstance(other, Clef):
            return self.midi == other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __ne__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> bool:
        if isinstance(other, Pitch):
            return self.midi != other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi != other
        elif isinstance(other, Clef):
            return self.midi != other.value
        else:
            raise TypeError('Cannot compare Pitch and type {0}.'.format(type(other)))

    def __sub__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> Union[int, float]:
        if isinstance(other, Pitch):
            return self.midi - other.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return self.midi - other
        elif isinstance(other, Clef):
            return self.midi - other.value
        else:
            raise TypeError('Cannot subtract type {0} from Pitch.'.format(type(other)))

    def __rsub__(self, other: Union['Pitch', float, np.inexact, int, np.integer, 'Clef']) -> Union[int, float]:
        if isinstance(other, Pitch):
            return other.midi - self.midi
        elif isinstance(other, (float, np.inexact, int, np.integer)):
            return other - self.midi
        elif isinstance(other, Clef):
            return other.value - self.midi
        else:
            raise TypeError('Cannot subtract Pitch from type {0}.'.format(type(other)))

    # ---------
    # Methods
    # ---------
    def freq(self) -> float:
        return 2 ** ((self.midi - 69) / 12) * 440

    def step_diff(self, other) -> int:
        if isinstance(other, Pitch):
            octave_diff = 7 * (self.octave - other.octave)
            step_diff = other.step.diff(self.step)
            print('diff', octave_diff, step_diff, octave_diff + step_diff)
            return octave_diff + step_diff
        else:
            raise TypeError('Cannot find difference between Pitch and type {0}.'.format(type(other)))

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_midi(cls, midi_pitch, key=None):
        # from numeric (midi)
        midi_pitch = int(midi_pitch)
        if midi_pitch > 128 or midi_pitch < 0:
            raise ValueError('Cannot match Pitch to MIDI value {0}.'.format(midi_pitch))

        # TODO use key info

        if Step.has_value(midi_pitch % 12):
            step = Step(midi_pitch % 12)
            return Pitch(step=step)
        else:
            step = Step(midi_pitch % 12 + 1)
            octave = Octave(midi_pitch // 12 - 1)
            return Pitch(step=step, octave=octave)

    @classmethod
    def from_abc(cls, abc_pitch):
        # default
        pitch = Pitch()

        # verify plausible abc pitch
        pitch_match = re.match('^([_^=]*[a-gA-G][\',]*)$', abc_pitch)
        if not pitch_match:
            raise ValueError('Cannot match Pitch in abc string {0}.'.format(abc_pitch))

        # accidental (optional)
        accidental_match = re.match('[_^=]+', abc_pitch)
        if accidental_match:
            pitch.alter = Accidental.from_abc(accidental_match.group())

        # step (required)
        octave_number = 4  # default value
        step_match = re.match('.*?([a-gA-G])', abc_pitch)
        if step_match:
            if step_match.group(1).isupper():
                octave_number = 4
            elif step_match.group(1).islower():
                octave_number = 5
            pitch.step = Step.from_str(step_match.group(1))
        else:
            raise ValueError('Cannot match Pitch in abc string {0}.'.format(abc_pitch))

        # octave adjustment (optional)
        octave_match = re.match('.*?([\',]+)', abc_pitch)
        if octave_match:
            for char in octave_match.group():
                if char == '\'':
                    octave_number += 1
                elif char == ',':
                    octave_number -= 1
            pitch.octave = Octave.from_int(octave_number)

        return pitch


# --------------
# Chromatic enum
# --------------
class Chromatic(Enum):
    """
    Enum to represent chromatic steps
    """

    Cbb = ('C double-flat', 'C𝄫', 'Ceses', Pitch(Step.C, alter=Accidental.DOUBLE_FLAT))
    Cb = ('C flat', 'C♭', 'Ces', Pitch(Step.C, alter=Accidental.FLAT))
    C = ('C', 'C', 'C', Pitch(Step.C, alter=Accidental.NONE))
    Cs = ('C sharp', 'C♯', 'Cis', Pitch(Step.C, alter=Accidental.SHARP))
    Css = ('C double-sharp', 'C𝄪', 'Cisis', Pitch(Step.C, alter=Accidental.DOUBLE_SHARP))

    Dbb = ('D double-flat', 'D𝄫', 'Deses', Pitch(Step.D, alter=Accidental.DOUBLE_FLAT))
    Db = ('D flat', 'D♭', 'Des', Pitch(Step.D, alter=Accidental.FLAT))
    D = ('D', 'D', 'D', Pitch(Step.D, alter=Accidental.NONE))
    Ds = ('D sharp', 'D♯', 'Dis', Pitch(Step.D, alter=Accidental.SHARP))
    Dss = ('D double-sharp', 'D𝄪', 'Disis', Pitch(Step.D, alter=Accidental.DOUBLE_SHARP))

    Ebb = ('E double-flat', 'E𝄫', 'Eeses', Pitch(Step.E, alter=Accidental.DOUBLE_FLAT))
    Eb = ('E flat', 'E♭', 'Es', Pitch(Step.E, alter=Accidental.FLAT))
    E = ('E', 'E', 'E', Pitch(Step.E, alter=Accidental.NONE))
    Es = ('E sharp', 'E♯', 'Eis', Pitch(Step.E, alter=Accidental.SHARP))
    Ess = ('E double-sharp', 'E𝄪', 'Eisis', Pitch(Step.E, alter=Accidental.DOUBLE_SHARP))

    Fbb = ('F double-flat', 'F𝄫', 'Feses', Pitch(Step.F, alter=Accidental.DOUBLE_FLAT))
    Fb = ('F flat', 'F♭', 'Fes', Pitch(Step.F, alter=Accidental.FLAT))
    F = ('F', 'F', 'F', Pitch(Step.F, alter=Accidental.NONE))
    Fs = ('F sharp', 'F♯', 'Fis', Pitch(Step.F, alter=Accidental.SHARP))
    Fss = ('F double-sharp', 'F𝄪', 'Fisis', Pitch(Step.F, alter=Accidental.DOUBLE_SHARP))

    Gbb = ('G double-flat', 'G𝄫', 'Geses', Pitch(Step.G, alter=Accidental.DOUBLE_FLAT))
    Gb = ('G flat', 'G♭', 'Ges', Pitch(Step.G, alter=Accidental.FLAT))
    G = ('G', 'G', 'G', Pitch(Step.G, alter=Accidental.NONE))
    Gs = ('G sharp', 'G♯', 'Gis', Pitch(Step.G, alter=Accidental.SHARP))
    Gss = ('G double-sharp', 'G𝄪', 'Gisis', Pitch(Step.G, alter=Accidental.DOUBLE_SHARP))

    Abb = ('A double-flat', 'A𝄫', 'Asas', Pitch(Step.A, alter=Accidental.DOUBLE_FLAT))
    Ab = ('A flat', 'A♭', 'As', Pitch(Step.A, alter=Accidental.FLAT))
    A = ('A', 'A', 'A', Pitch(Step.A, alter=Accidental.NONE))
    As = ('A sharp', 'A♯', 'Ais', Pitch(Step.A, alter=Accidental.SHARP))
    Ass = ('A double-sharp', 'A𝄪', 'Aisis', Pitch(Step.A, alter=Accidental.DOUBLE_SHARP))

    Bbbb = ('B double-flat', 'B♭𝄫', 'Heseses', Pitch(Step.B, alter=Accidental.TRIPLE_FLAT))
    Bbb = ('B double-flat', 'B𝄫', 'Heses', Pitch(Step.B, alter=Accidental.DOUBLE_FLAT))
    Bb = ('B flat', 'B♭', 'Bb', Pitch(Step.B, alter=Accidental.FLAT))
    B = ('B', 'B', 'H', Pitch(Step.B, alter=Accidental.NONE))
    Bs = ('B sharp', 'B♯', 'His', Pitch(Step.B, alter=Accidental.SHARP))
    Bss = ('B double-sharp', 'B𝄪', 'Hisis', Pitch(Step.B, alter=Accidental.DOUBLE_SHARP))

    # -----------
    # Constructor
    # -----------
    def __init__(self, long_name, abbr, de_name, pitch):
        self.long_name = long_name
        self.abbr = abbr
        self.de_name = de_name
        self.pitch = pitch

    # ----------
    # Properties
    # ----------

    # --------
    # Override
    # --------
    def __str__(self):
        return self.abbr

    def __repr__(self):
        return '<{self.__class__.__name__}({self.long_name})>'.format(self=self)

    # ---------
    # Methods
    # ---------
    def pitch(self):
        return self.pitch

    # -------------
    # Class Methods
    # -------------

    # from string, use movable do https://en.wikipedia.org/wiki/Solf%C3%A8ge
