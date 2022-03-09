import warnings
from enum import Enum

from musicai.structure.note_mark import StemType, DynamicType
from musicai.structure.clef import Clef
from musicai.structure.time import TimeSignature, TempoType, Tempo
from musicai.structure.note import Note, Rest
from musicai.structure.pitch import Pitch, Step, Accidental
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
    note_connected = False

    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0,  # relative to the start of measure
                 end_time: Union[float, int, np.inexact, np.integer] = 0.0):  # relative to the start of measure
        self.start_time = start_time
        self.end_time = end_time
        self._duration_ = end_time - start_time

        # Find out if it's connected to a note, and if so, then tie it to that note

    # -----------
    # Overrides
    # -----------
    def __str__(self) -> str:
        return self.mark_name + ' ' + self.value_name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__.title()}({self.value_name})>'

    # -----------
    # Properties
    # -----------
    @property
    def duration(self):
        return self._duration_

    @duration.setter
    def duration(self, value: Union[float, int, np.inexact, np.integer]):
        if value == 0:
            raise ValueError(f'The measure marking {str(self)} cannot have a duration of 0')
        else:
            self._duration_ = value
            self.end_time = self.start_time + value

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
    DECRESCENDO = -1.0
    CRESCENDO = 1.0


# ---------------------
# HairpinType enum
# ---------------------
class HairpinType(Enum):
    """
    Enum to represent types of hairpins
    """
    STANDARD = 0
    SILENCED = 1  # from silence or to silence
    DASHED = 2
    DOTTED = 3
    BRACKETED = 4


# ---------------------
# TempoChangeType enum
# ---------------------
class TempoChangeType(Enum):
    """
    Enum to represent the change in tempo
    """
    RITARDANDO = 0.3  # TODO: update values
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
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_time: Union[float, int, np.inexact, np.integer] = 0.0):
        MeasureMark.__init__(self, start_time, end_time)
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
                 dynamic_change_type: DynamicChangeType = DynamicChangeType.CRESCENDO,
                 intensity: Intensity = Intensity.STANDARD,
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 hairpin: bool = True,
                 hairpin_type: HairpinType = HairpinType.STANDARD):

        MeasureMark.__init__(self, start_time, end_time)
        self.dynamic_change_type = dynamic_change_type
        self.intensity = intensity
        self.hairpin = hairpin
        self.hairpin_type = hairpin_type
        self.value_name = dynamic_change_type.name.title()


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
                 octave_change: Union[int, str, float, np.inexact, np.integer] = 0,
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 vertical_dotted_line: bool = False):
        MeasureMark.__init__(self, start_time, end_time)

        if isinstance(octave_change, str):
            self.octave_change = self.octave_change_from_str(octave_change)
        else:
            self.octave_change = int(octave_change)
            if int(octave_change) != octave_change:
                warnings.warn(f'Warning: Octave change was shifted from {octave_change} to {int(octave_change)}')

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
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 end_time: Union[float, int, np.inexact, np.integer] = 0.0,
                 damper_release_sign: bool = False,
                 vertical_dotted_line: bool = False,
                 half_pedalling: tuple = None  # tuples of time stamps and pedal intensities to use across the duration
                 ):
        MeasureMark.__init__(self, start_time, end_time)

        self.pedal_type = pedal_type
        self.damper_release_sign = damper_release_sign
        self.vertical_dotted_line = vertical_dotted_line
        self.half_pedalling = half_pedalling
        self.value_name = pedal_type.name.title()


# ---------------------
# InstantaneousMeasureMark Class
# ---------------------
class InstantaneousMeasureMark(MeasureMark):
    """
    Class to represent common instantaneous notation in a measure
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 start_time: Union[float, int, np.inexact, np.integer, tuple] = 0.0):

        if isinstance(start_time, tuple):  # custom case where an "instantaneous" measure mark has a different end time
            MeasureMark.__init__(self, start_time[0], start_time[1])
        else:
            MeasureMark.__init__(self, start_time, start_time)

    # -----------
    # Overrides
    # -----------
    @property
    def duration(self):
        return self._duration_

    @duration.setter
    def duration(self, value: Union[float, int, np.inexact, np.integer]):
        self._duration_ = value
        self.end_time = self.start_time + value


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
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0):

        InstantaneousMeasureMark.__init__(self, start_time)  # instantaneous, so start time = end time

        if isinstance(tempo_type, TempoType):  # Make a tempo from the common tempo types
            self.tempo = Tempo(tempo_type.value, tempo_type)
        elif isinstance(tempo_type, str):  # Find a tempo given a string
            self.tempo = Tempo.find(tempo_type)
        else:
            self.tempo = tempo_type

        self.value_name = self.tempo.tempo_name


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
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0):
        InstantaneousMeasureMark.__init__(self, start_time)
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
    BREATH_MARK = 1, u'\U0001D112'  # aka luftpause

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj.value = values[0]
        obj.symbol = values[1]
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
                 start_time: Union[float, int, np.inexact, np.integer] = 0.0):
        InstantaneousMeasureMark.__init__(self, start_time)
        self.mark_type = misc_mark_type
        self.value_name = misc_mark_type.name.title()
