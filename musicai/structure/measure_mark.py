import warnings
from enum import Enum

from structure.note_mark import StemType
from structure.clef import Clef
from structure.time import TimeSignature, TempoType, Tempo
from structure.note import Note, Rest
from structure.pitch import Pitch, Step, Accidental
from typing import Union
import numpy as np


# ---------------------
# MeasureMark class
# ---------------------
class MeasureMark:
    """
    Class to represent common line notation in / throughout a measure
    """
    mark_name = ''  # Common attributes to be initialized in child classes (will test this happens)
    value_name = ''  # value_name is used for repr()
    symbol = ''

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False,
                 divisions: Union[int, np.inexact] = 256
                 ):
        """
        Sets the values of a Measure Mark instance.

        :param start_point: Where the measure mark starts, relative to the beginning of measure. One unit describes
            1 / divisions of a quarter note.

        :param end_point: Where the measure mark ends, relative to the beginning of a measure. If the mark spans
            multiple measures, then it is relative to the beginning of the measure 'measure_span' in front of this in
            the part. One unit describes 1 / divisions of a quarter note.

        :param note_connected: Whether or not this marking's position is anchored to a note.  # TODO: remove this?
        :param divisions: Provides basis for start_point and end_point--acts as the denominator.
        """
        self.start_point = start_point
        self.end_point = end_point
        self._duration_ = end_point - start_point
        self.note_connected = note_connected
        self.divisions = divisions

        self.number = None  # used to distinguish overlapping elements
        self.measure_index = 0
        self.measure_span = 0

        # Find out if it's connected to a note, and if so, then link it to that note
        if note_connected:
            pass

    # -----------
    # Overrides
    # -----------
    def __str__(self) -> str:
        return self.mark_name + ' ' + self.value_name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__.title()}({self.value_name}) start:{self.start_point} end:{self.end_point}' \
               f' measure_span:{self.measure_span} divs:{self.divisions}>'

    # -----------
    # Properties
    # -----------
    @property
    def duration(self):
        return self._duration_

    @duration.setter
    def duration(self, value: Union[float, int, np.inexact, np.integer]):
        if value == 0:
            raise ValueError(
                f'The measure marking {str(self)} cannot have a duration of 0')
        else:
            self._duration_ = value
            self.end_point = self.start_point + value

    # -----------
    # Methods
    # -----------
    def update_position(self):
        pass

    # -----------
    # Class Methods
    # -----------


# ---------------------
# Intensity enum
# ---------------------
class Intensity(Enum):
    """
    Enum to represent the intensities of line markings and standard multiplier values
    """
    POCO = 0.5
    STANDARD = 1.0
    MOLTO = 2.0


# ---------------------
# DynamicChangeType enum
# ---------------------
class DynamicChangeType(Enum):
    """
    Enum to represent the change in dynamics
    """
    DIMINUENDO = -1.0
    CRESCENDO = 1.0


# ---------------------
# HairpinType enum
# ---------------------
class HairpinType(Enum):
    """
    Enum to represent types of hairpins
    """
    NONE = 0
    STANDARD = 1
    DASHED = 2
    DOTTED = 3
    WAVY = 4
    BRACKETED = 5


# ---------------------
# TempoChangeType enum
# ---------------------
class TempoChangeType(Enum):
    """
    Enum to represent the change in tempo
    """
    RITARDANDO = 0.3  # TODO: update values from the book
    RALLENTANDO = 0.5
    ACCELERANDO = 1.5


# ---------------------
# TempoChangeMark class
# ---------------------
class TempoChangeMark(MeasureMark):
    """
    Class to represent a dynamic change between points in a measure
    """
    mark_name = 'Tempo Change'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 tempo_change_type: TempoChangeType = TempoChangeType.RITARDANDO,
                 intensity: Intensity = Intensity.STANDARD,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False):
        MeasureMark.__init__(self, start_point, end_point, note_connected)
        self.tempo_change_type = tempo_change_type
        self.intensity = intensity
        self.value_name = tempo_change_type.name.title()


# ---------------------
# DynamicChangeMark class
# ---------------------
class DynamicChangeMark(MeasureMark):
    """
    Class to represent a dynamic change between points in a measure
    """
    mark_name = 'Dynamic Change'

    # -----------
    # Constructor
    # -----------
    def __init__(self,  # TODO: make the starting condition types more generalized (like can take in str)
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 dynamic_change_type: Union[DynamicChangeType,
                                            str] = DynamicChangeType.CRESCENDO,
                 intensity: Union[Intensity, str] = Intensity.STANDARD,
                 hairpin: bool = True,
                 hairpin_type: Union[HairpinType, str] = HairpinType.STANDARD,
                 niente: Union[bool, str, None] = False,
                 divisions: Union[int, np.integer] = 256):
        MeasureMark.__init__(self, start_point, end_point, False, divisions)

        if isinstance(dynamic_change_type, str):
            if dynamic_change_type.upper() in [dct.name for dct in DynamicChangeType]:
                self.dynamic_change_type = DynamicChangeType[dynamic_change_type.upper(
                )]
            else:
                raise ValueError(
                    f'\'{dynamic_change_type}\' is not a valid Dynamic Change Type.')
        elif isinstance(dynamic_change_type, DynamicChangeType):
            self.dynamic_change_type = dynamic_change_type
        else:
            raise TypeError(f'Cannot make a DynamicChangeMark with change type {dynamic_change_type} '
                            f'of type {type(dynamic_change_type)}.')

        if isinstance(intensity, str):
            if intensity.upper() in [i.name for i in Intensity]:
                self.intensity = Intensity[intensity.upper()]
            else:
                raise ValueError(f'\'{intensity}\' is not a valid Intensity.')
        elif isinstance(intensity, Intensity):
            self.intensity = Intensity
        else:
            raise TypeError(
                f'Cannot make DynamicChangeMark with intensity {intensity} of type {type(intensity)}.')

        self.hairpin = hairpin

        if isinstance(hairpin_type, str):
            if hairpin_type.upper() in [ht.name for ht in HairpinType]:
                self.hairpin_type = HairpinType[hairpin_type.upper()]
            else:
                raise ValueError(
                    f'\'{hairpin_type}\' is not a valid Hairpin Type.')
        elif isinstance(hairpin_type, HairpinType):
            self.hairpin_type = HairpinType
        else:
            raise TypeError(
                f'Cannot make DynamicChangeMark with hairpin {hairpin_type} of type {type(hairpin_type)}.')

        if isinstance(niente, str):
            if niente.lower() == 'yes':
                self.niente = True
            elif niente.lower() == 'no':
                self.niente = False
            else:
                raise ValueError(
                    f'Cannot make a DynamicChangeMark with niente of value {niente}.')
        elif isinstance(niente, bool):
            self.niente = niente
        elif niente is None:
            self.niente = False
        else:
            raise TypeError(
                f'Cannot make a DynamicChangeMark with niente of type {type(niente)}.')

        self.value_name = self.dynamic_change_type.name.title()

    # -----------
    # Overrides
    # -----------
    def __str__(self):
        match self.dynamic_change_type:
            case DynamicChangeType.DIMINUENDO:
                return u'\U0001D193'  # Diminuendo Symbol
            case _:
                return u'\U0001D192'  # Crescendo Symbol


# ---------------------
# OctaveLineMark class
# ---------------------
class OctaveLineMark(MeasureMark):
    """
    Class to represent an octave line across a measure (not a single note line)
    """
    mark_name = 'Octave Line'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 octave_change: Union[int, str, float,
                                      np.inexact, np.integer] = 0,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False,
                 vertical_dotted_line: bool = False):
        MeasureMark.__init__(self, start_point, end_point, note_connected)

        if isinstance(octave_change, str):
            self.octave_change = self.octave_change_from_str(octave_change)
        else:
            self.octave_change = int(octave_change)
            if int(octave_change) != octave_change:
                warnings.warn(
                    f'Warning: Octave change was shifted from {octave_change} to {int(octave_change)}')

        self.vertical_lines = vertical_dotted_line
        self.value_name = f'{self.octave_change} octaves'

    # -----------
    # Class Methods
    # -----------
    @classmethod
    def octave_change_from_str(cls, value: str) -> int:
        # checks for the most common octave changes first, checking the value without spaces or underscores
        match value.lower().replace(' ', '').replace('_', ''):
            case '8up': return 1
            case '8vaup': return 1
            case 'ottavasopra': return 1
            case '8down': return -1
            case '8vadown': return -1
            case 'ottavabassa': return -1
            case '15up': return 2
            case '15maup': return 2
            case '15down': return -2
            case '15madown': return -2
            case '22up': return 3
            case '22maup': return 3
            case '22down': return -3
            case '22madown': return -3

        # checks to see if value is an integer (there can be no decimal points and only one '-')
        if value.replace('-', '').isnumeric() and value.count('-') < 2:
            return int(value)

        return 0


# # ---------------------   GLISSANDOS WILL BE USED AS INTERNOTE MARKINGS
# # GlissandoType enum
# # ---------------------
# class GlissandoType(Enum):
#     """
#     Enum to represent ways to notate glissanndi
#     """
#     STRAIGHT = 0  # glissando typically refers to a more deliberate, continous slide
#     WAVY = 1
#     PORTAMENTO = 2  # typically, meant to indicate an expressive legato slide a smooth, microtonal slide
#
#
# # ---------------------
# # GlissandoMark class
# # ---------------------
# class GlissandoMark(MeasureMark):
#     """
#     Class to represent glissando slide notation
#     """
#     mark_name = 'Glissando'
#
#     # -----------
#     # Constructor
#     # -----------
#     def __init__(self,
#                  start_time: Union[float, int, np.inexact, np.integer] = 0.0,
#                  end_time: Union[float, int, np.inexact, np.integer] = 0.0,
#                  note_connected: bool = False,
#                  glissando_type: GlissandoType = GlissandoType.STRAIGHT):
#         MeasureMark.__init__(self, start_time, end_time, note_connected)
#
#         if glissando_type == GlissandoType.PORTAMENTO:
#             self.mark_name = 'Portamento'
#             self.value_name = 'Straight'
#
#         else:
#             self.value_name = glissando_type.name.title()


# ---------------------
# PedalType enum
# ---------------------
class PedalType(Enum):
    """
    Enum to represent types of pedalling in keyboard notation
    """
    NONE = 0, ''
    DAMPER = 1, 'sustaining'
    SOSTENUTO = 2, 'middle'
    UNA_CORDA = 3, 'soft'  # released with 'tre corde'
    SENZA_PEDALE = 4, 'no use'
    CON_PEDALE = 5, 'may be used'  # AKA col pedale

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.category = values[1]
        return obj


# ---------------------
# PedalMark class
# ---------------------
class PedalMark(MeasureMark):
    """
    Class to represent pedal markings, typically for keyboard
    """
    mark_name = 'Pedal'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 pedal_type: PedalType = PedalType.NONE,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 damper_release_sign: bool = False,
                 vertical_dotted_line: bool = False,
                 note_connected: bool = False,
                 # tuples of time stamps and pedal intensities to use across the duration
                 half_pedalling: tuple = None
                 ):
        MeasureMark.__init__(self, start_point, end_point, note_connected)

        self.pedal_type = pedal_type
        self.damper_release_sign = damper_release_sign
        self.vertical_dotted_line = vertical_dotted_line
        self.half_pedalling = half_pedalling
        self.value_name = pedal_type.name.title()


# ---------------------
# VoltaBracketType class
# ---------------------
class VoltaBracketType(Enum):
    """
    Class to represent if the ending bracket is open or closed
    """
    CLOSED = 0,
    OPEN = 1


# ---------------------
# VoltaBracketMark class
# ---------------------
class VoltaBracketMark(MeasureMark):
    """
    Class to represent 1st, 2nd, 3rd, etc. endings used around repeat symbols
    """
    mark_name = 'Volta Bracket'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 # tuple is used if a passage counts for many endings
                 ending_count: Union[int, np.integer, tuple] = 0,
                 volta_bracket_type: VoltaBracketType = VoltaBracketType.CLOSED,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False):
        MeasureMark.__init__(self, start_point, end_point, note_connected)

        self.ending_count = ending_count
        self.volta_bracket_type = volta_bracket_type


# ---------------------
# InstantaneousMeasureMark Class
# ---------------------
class InstantaneousMeasureMark(MeasureMark):
    """
    Class to represent common instantaneous notation in a measure
    ! May be depreceated since some non-IMM's have duration 0 --> just make all IMM's an MM with duration = 0 !
    """
    # -----------
    # Constructor
    # -----------

    def __init__(self,
                 start_point: Union[float, int,
                                    np.inexact, np.integer, tuple] = 0.0,
                 note_connected: bool = False):

        # custom case where an "instantaneous" measure mark has a different end time
        if isinstance(start_point, tuple):
            MeasureMark.__init__(self, start_point[0], start_point[1])
        else:
            MeasureMark.__init__(self, start_point, start_point)

        self.note_connected = note_connected

    # -----------
    # Overrides
    # -----------
    @property
    def duration(self):
        return self._duration_

    @duration.setter
    def duration(self, value: Union[float, int, np.inexact, np.integer]):
        self._duration_ = value
        self.end_time = self.start_point + value


# ---------------------
# TempoMark class
# ---------------------
class TempoMark(InstantaneousMeasureMark):
    """
    Class to represent an instantaneous definition of tempo
    """
    mark_name = 'Tempo'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 tempo_type: Union[TempoType, Tempo, str] = TempoType.NONE,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False):

        InstantaneousMeasureMark.__init__(self, start_point, note_connected)

        if isinstance(tempo_type, TempoType):  # Make a tempo from the common tempo types
            self.tempo = Tempo(tempo_type.value, tempo_type)
        elif isinstance(tempo_type, str):  # Find a tempo given a string
            self.tempo = Tempo.find(tempo_type)
        else:
            self.tempo = tempo_type

        self.value_name = self.tempo.tempo_name


# ----------------
# DynamicType enum
# ----------------
class DynamicType(Enum):
    NONE = 0, 0, '', ''
    PIANISSISSISSIMO = 1, 10, 'pppp', '\U0001D18F\U0001D18F\U0001D18F\U0001D18F'
    PIANISSISSIMO = 2, 23, 'ppp', '\U0001D18F\U0001D18F\U0001D18F'
    PIANISSIMO = 3, 36, 'pp', '\U0001D18F\U0001D18F'
    PIANO = 4, 49, 'p', '\U0001D18F'
    MEZZOPIANO = 5, 62, 'mp', '\U0001D190\U0001D18F'
    MEZZOFORTE = 6, 75, 'mf', '\U0001D190\U0001D191'
    FORTE = 7, 88, 'f', '\U0001D191'
    FORTISSIMO = 8, 101, 'ff', '\U0001D191\U0001D191'
    FORTISSISSIMO = 9, 114, 'fff', '\U0001D191\U0001D191\U0001D191'
    FORTISSISSISSIMO = 10, 127, 'ffff', '\U0001D191\U0001D191\U0001D191\U0001D191'

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.velocity = values[1]
        obj.abbr = values[2]
        obj.symbol = values[3]
        obj._all_values = values
        return obj


# ---------------------
# DynamicMark class
# ---------------------
class DynamicMark(InstantaneousMeasureMark):
    """
    Class to represent an instantaneous definition of dynamics
    """
    mark_name = 'Dynamic'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 dynamic_type: DynamicType = DynamicType.NONE,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False):
        InstantaneousMeasureMark.__init__(self, start_point, note_connected)
        self.dynamic_type = dynamic_type
        self.value_name = self.dynamic_type.name.title()
    # TODO: implement overrides / conversions, and (?) multipliers


# ---------------------
# MiscMarkType enum
# ---------------------
class MiscMarkType(Enum):
    """
    Enum to represent common miscellaneous marks throughout measures
    """
    NONE = -1, ''
    CAESURA = 0, u'\U0001D113'  # railroad tracks
    BREATH_MARK = 1, u'\U0001D112'  # AKA luftpause

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.symbol = values[1]
        obj._all_values_ = values
        return obj


# ---------------------
# MiscMark class
# ---------------------
class MiscMark(InstantaneousMeasureMark):
    """
    Class to represent miscellaneous marks used throughout measures
    """
    mark_name = 'Miscellaneous'

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 misc_mark_type: MiscMarkType = MiscMarkType.NONE,
                 start_point: Union[float, int, np.inexact, np.integer] = 0.0,
                 note_connected: bool = False):
        InstantaneousMeasureMark.__init__(self, start_point, note_connected)
        self.mark_type = misc_mark_type
        self.value_name = misc_mark_type.name.title()
