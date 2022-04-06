import re
import warnings
from enum import Enum
import numpy as np
from typing import Union

from musicai.structure.note_mark import StemType
from musicai.structure.measure_mark import MeasureMark
from musicai.structure import measure_mark
from musicai.structure.clef import Clef
from musicai.structure.key import Key
from musicai.structure.time import TimeSignature
from musicai.structure.note import Note, Rest
from musicai.structure.pitch import Accidental


# ----------------
# BarlineType enum
# ----------------
class BarlineType(Enum):
    NONE = 0, '', ''
    SHORT = 1, '\U0001D105', 'barlineShort'
    TICK = 2, '\U0001D105', 'barlineTick'
    REGULAR = 3, '\U0001D100', 'barlineSingle'
    DOUBLE = 4, '\U0001D101', 'barlineDouble'
    FINAL = 5, '\U0001D102', 'barlineFinal'
    REVERSE_FINAL = 5, '\U0001D103', 'barlineReverseFinal'
    HEAVY = 6, '\U0001D100\U0001D100\U0001D100', 'barlineHeavy'
    DOUBLE_HEAVY = 7, '\U0001D100\U0001D100\U0001D100\u0020\U0001D100\U0001D100\U0001D100', 'barlineHeavyHeavy'
    DASHED = 8, '\U0001D104', 'barlineDashed'
    DOTTED = 9, '\U0001D104', 'barlineDotted'
    INVISIBLE = 10, '', ''

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.symbol = values[1]
        obj.glyph = values[2]
        obj._all_values = values
        return obj

    # -----------
    # Overrides
    # -----------
    def __str__(self):
        return self.symbol

    # -----------
    # Methods
    # -----------

    # -----------
    # Class Methods
    # -----------
    @classmethod
    def from_str(cls, value: str) -> Union['BarlineType', None]:
        value = ''.join(filter(str.isalpha, value)).upper()

        if value in [bt.name for bt in BarlineType]:
            return BarlineType[value]
        else:
            # warnings.warn(f'Barline {value.title()} does not exist--returning BarlineType.NONE', stacklevel=2)
            return None


# --------------------
# BarlineLocation enum
# --------------------
class BarlineLocation(Enum):
    NONE = 0
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3


# -------------
# Barline class
# -------------
class Barline:
    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 barlinetype: BarlineType = BarlineType.REGULAR,
                 barlinelocation: BarlineLocation = BarlineLocation.RIGHT):
        self.barlinetype = barlinetype
        self.barlinelocation = barlinelocation
        self.left_repeat = 0
        self.right_repeat = 0

    # ----------
    # Properties
    # ----------

    # --------
    # Override
    # --------
    def __str__(self) -> str:
        return str(self.barlinetype)

    # ---------
    # Methods
    # ---------

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls, abc_barline):
        abc_barline = abc_barline.strip()
        if not re.match('^[\|\[\]\:\.]+$', abc_barline):
            raise ValueError(f'Cannot match abc string \'{abc_barline}\' to a Barline')
        else:
            if abc_barline == '|':
                barlinetype = BarlineType.REGULAR
            elif abc_barline == '||':
                barlinetype = BarlineType.DOUBLE
            elif abc_barline == '[|':
                barlinetype = BarlineType.REVERSE_FINAL
            elif abc_barline == '|]':
                barlinetype = BarlineType.FINAL
            elif abc_barline == '|]':
                barlinetype = BarlineType.FINAL
            elif abc_barline == '[|]':
                barlinetype = BarlineType.INVISIBLE


# -------------
# MeasureStyle Enum
# -------------
class MeasureStyle(Enum):
    NONE = None
    MULTIPLE_REST = 0
    MEASURE_REPEAT = 1
    BEAT_REPEAT = 2
    SLASH = 3
    # TODO: implement how this will work with Score, get_note functions and etc.


# -------------
# Measure class
# -------------
class Measure:
    """
    Class to represent a Measure
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self, measure_number=-1, time=TimeSignature(), key=Key(), clef=Clef()):
        self.measure_number = measure_number
        self.notes = []
        self.time = time
        self.clef = clef
        self.key = key
        self.barline: Union[Barline, BarlineType] = BarlineType.REGULAR
        self.is_full = False
        self.remaining = 1.0
        self.display_clef = False
        self.display_time = False
        self.display_key = False
        self.measure_style = MeasureStyle.NONE
        self.measure_marks: list[MeasureMark] = []

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for note in self.notes:
            if note is None:
                raise ValueError('note is None')
            ret_str += str(note) + ' '
        ret_str += str(self.barline)
        # ret_str += ' ' + ''.join([str(barline) for barline in self.barlines])
        return ret_str

    def __len__(self):
        return len(self.notes)

    # ---------
    # Methods
    # ---------
    def append(self, notes):
        # TODO add checks for measure full
        # TODO fix timing
        # TODO add list of notes

        if isinstance(notes,  (list, tuple)):
            for note in notes:
                self.stem_note(note)
                self.notes.append(note)
        elif isinstance(notes, Rest):
            self.notes.append(notes)
        elif isinstance(notes, Note):
            self.stem_note(notes)
            self.notes.append(notes)
        else:
            raise TypeError(f'Cannot add type {type(notes)} to Measure')
        self.pack()

        # NOW, ADJUST THE NOTE'S LOCATION

    def append_at(self,
                  location: Union[int, np.integer, float, np.inexact],
                  notes: Union[Note, list[Note], tuple[Note]],
                  division: Union[int, np.integer] = 1024):

        # Check for if there is a note ON the start location or DURING the start location,
        # what is present at the note's start location
        pass

    def stem_note(self, note):  # TODO: update to match notation rules
        if note.pitch < self.clef:
            # stem up
            note.stem = StemType.UP
        else:
            # stem down
            note.stem = StemType.DOWN

    def stem(self):
        for note in self.notes:
            self.stem_note(note)

    def set_accidentals(self):
        for note in self.notes:
            if self.key.has_accidental(note.midi):
                note.show_accidental = True
                if note.accidental is None or note.accidental is Accidental.NONE:
                    # natural
                    note.accidental = Accidental.NATURAL
            pass

    def set_barline(self, value: Union[Barline, BarlineType, str]):
        if isinstance(value, str):
            if (bt := BarlineType.from_str(value)) is not None:
                self.barline = bt
            else:
                warnings.warn(f'"{value.title()}" is not a valid barline type--defaulting to Barlines.REGULAR.',
                              stacklevel=2)
                self.barline = BarlineType.REGULAR

        elif isinstance(value, Union[BarlineType, Barline]):
            self.barline = value

        else:
            raise TypeError(f'Cannot set a barline using type {type(value)}.')

    def beam(self):
        print("BEAMING")
        # never beam over middle beat
        # time_signature_value = self.time.value
        #
        # time = 0
        # # first half of measure
        # idx = 0
        # while time < time_signature_value / 2:
        #     note = self.notes[idx]
        #     time += note.value
        #     idx+=1
        #     #if note.value
        #
        #
        #     print('beaming', note, time)

        # second half of measure

    def min(self):
        return min(self.notes).value

    def max(self):
        return max(self.notes).value

    def sum(self):
        return sum(self.notes)

    def len(self):
        return self.time.numerator / self.time.denominator

    def count(self):
        return len(self.notes)

    def pack(self):
        # determine note times
        time = 0
        for note in self.notes:
            note.start_time = time
            time += note.value
        #if time > 1:
        #    raise NotImplementedError
        #elif time == 1.0:
        #    self.is_full = True
        #else:
        #    self.remaining = 1.0 - time


        # if self.is_full:
        #     raise NotImplementedError
        # else:
        #     if note.start == -1:
        #         # add note at end
        #         note.end = self.notes[-1].start
        #         self.notes.append(note)
        #     else:
        #         raise NotImplementedError

        self.beam()

    def get_note(self, location: Union[int, np.integer, float, np.inexact]) -> Note:

        # If there's an OCTAVE LINE MARK over the note, let that impact
        # the note you return

        # check if_over_note(measure_mark, note) for octave lines

        pass

    def insert_tempo_change(self):
        pass

    def insert_dynamic_change(self,
                              start_point: Union[int, np.integer, np.inexact, float] = 0,
                              end_point: Union[int, np.integer, np.inexact, float] = 0,
                              dynamic_change_type: str = 'crescendo',
                              intensity: str = 'standard',
                              hairpin: bool = True,
                              hairpin_type: str = '',
                              divisions: Union[int, np.integer] = 1024):

        dc = measure_mark.DynamicChangeMark(start_point, end_point, dynamic_change_type, intensity, hairpin,
                                            hairpin_type, divisions)
        self.measure_marks.append(dc)

    def insert_octave_line(self):
        pass

    def insert_pedal(self):
        pass

    def insert_volta_bracket(self):
        pass

    def insert_tempo(self):
        pass

    def insert_dynamic(self):
        pass

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls):
        pass
