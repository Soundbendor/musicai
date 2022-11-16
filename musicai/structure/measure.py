import re
import warnings
from enum import Enum
import numpy as np
from typing import Union

from structure.note_mark import StemType
from structure.measure_mark import MeasureMark
from structure import measure_mark
from structure.clef import Clef
from structure.key import Key
from structure.time import TimeSignature, Tempo
from structure.note import Note, Rest
from structure.pitch import Accidental


# ----------------
# BarlineType enum
# ----------------
class BarlineType(Enum):
    """
    An enum to represent BarlineTypes. An instance of this enum by itself, outside a Barline class, will
    always represent a right-sided barline

    """
    NONE = 0, '', ''
    SHORT = 1, u'\U0001D105', 'barlineShort'
    TICK = 2, u'\U0001D105', 'barlineTick'
    REGULAR = 3, u'\U0001D100', 'barlineSingle'
    DOUBLE = 4, u'\U0001D101', 'barlineDouble'
    FINAL = 5, u'\U0001D102', 'barlineFinal'
    REVERSE_FINAL = 5, u'\U0001D103', 'barlineReverseFinal'
    HEAVY = 6, u'\U0001D100\U0001D100\U0001D100', 'barlineHeavy'
    DOUBLE_HEAVY = 7, u'\U0001D100\U0001D100\U0001D100\u0020\U0001D100\U0001D100\U0001D100', 'barlineHeavyHeavy'
    DASHED = 8, u'\U0001D104', 'barlineDashed'
    DOTTED = 9, u'\U0001D104', 'barlineDotted'
    LEFT_REPEAT = 10, u'\U0001D106', 'leftRepeat'
    RIGHT_REPEAT = 11, u'\U0001D107', 'rightRepeat'
    INVISIBLE = 12, '', ''

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
    def is_simple_final_barline(self) -> bool:
        """
        Used to distunguish between final barlines

        :return:
        """
        if self.barlinetype == BarlineType.FINAL and self.barlinelocation == BarlineLocation.RIGHT \
                and self.right_repeat == 0:
            return True
        else:
            return False

    def is_regular(self) -> bool:
        """
        Used to distunguish regular barlines

        """
        if self.barlinetype == BarlineType.REGULAR and self.barlinelocation == BarlineLocation.RIGHT:
            return True
        else:
            return False

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls, abc_barline):
        abc_barline = abc_barline.strip()
        if not re.match('^[\|\[\]\:\.]+$', abc_barline):
            raise ValueError(
                f'Cannot match abc string \'{abc_barline}\' to a Barline')
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
# Transposition class
# -------------
class Transposition:
    """
    Class to represent automatically-applied transpositions to a measure
    """
    # -----------
    # Constructor
    # -----------

    def __init__(self,
                 diatonic: int | np.integer = 0,
                 chromatic: int | np.integer = 0,
                 octave_change: int | np.integer = 0,
                 doubled: bool = False):

        self.diatonic: int | np.integer = diatonic
        self.chromatic: int | np.integer = chromatic
        self.octave_change: int | np.integer = octave_change
        self.doubled: bool = doubled

    # -----------
    # Methods
    # -----------
    def is_equivilant(self, other: 'Transposition') -> bool:
        """
        Tells whether this is notationally equivilant to another Transposition object. This is based on if the two
        objects have the same attributes

        :param other: The other Transposition object to compare to the current one
        :return: Bool describing if they are notationally equivilant or not. Based on their attributes
        """
        if isinstance(other, Transposition):
            if vars(self) == vars(other):
                return True
            else:
                return False

        else:
            return False


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

    def __init__(self,
                 measure_number: Union[int, np.integer] = -1,
                 time: TimeSignature = TimeSignature(),
                 key: Key = Key(),
                 clef: Clef = Clef(),
                 barline=BarlineType.REGULAR):

        self.measure_number: int | np.integer = measure_number
        self.measure_marks: list[MeasureMark] = []
        self.notes: list[Note] = []

        self.time: TimeSignature | None = time
        self.clef: Clef | None = clef
        self.key: Key | None = key
        # self.tempo: Tempo | None = None  # Currently only one tempo is supported in the Score class
        self.transposition: Transposition | None = Transposition()
        self.divisions: int | np.integer = 256

        self.barline: Barline | BarlineType | list[Barline,
                                                   BarlineType] = barline

        # TODO: Implement...
        self.is_full: bool = False
        self.remaining = 1.0
        self.display_clef = False
        self.display_time = False
        self.display_key = False
        self.measure_style = MeasureStyle.NONE

    # --------
    # Override
    # --------
    def __str__(self) -> str:
        current_musical_pos = 0  # Used to dictate MeasureMark position
        mm_to_print = self.measure_marks.copy()
        ret_str = ''

        # Print every note and measure mark
        for note in self.notes:

            # Append the MeasureMark if it's at or behind the current note
            for mm in mm_to_print:
                if mm.start_point <= current_musical_pos:
                    # Print the mark and remove it from the list
                    ret_str += str(mm) + ' '
                    mm_to_print.remove(mm)

            # Append the note itself
            if note is None:
                raise ValueError('note is None')
            ret_str += str(note) + ' '

            # Update the current musical location
            current_musical_pos += (note.value.value * 4) * note.division

        # if isinstance(self.barline, list):
        #     ret_str += [str(barline) for barline in self.barlines]
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
            # self.stem_note(notes) TODO: Automatic note stemming
            self.notes.append(notes)
        else:
            raise TypeError(f'Cannot add type {type(notes)} to Measure')
        self.pack()

        # NOW, ADJUST THE NOTE'S LOCATION

    def append_at(self,
                  location: Union[int, np.integer, float, np.inexact],
                  notes: Union[Note, list[Note], tuple[Note]],
                  division: Union[int, np.integer] = 1024):

        # Must be aware if an octave measure marking exists at this point

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
        pass
        # print("BEAMING")
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
            note.start_point = time
            time += note.value
        # if time > 1:
        #    raise NotImplementedError
        # elif time == 1.0:
        #    self.is_full = True
        # else:
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

    def set_note(self):
        pass

    def print_measure_marks(self):
        print([repr(mm) for mm in self.measure_marks])

    def insert_tempo_change(self):
        pass

    def insert_dynamic_change(self,
                              start_point: Union[int, np.integer,
                                                 np.inexact, float] = 0,
                              end_point: Union[int, np.integer,
                                               np.inexact, float] = 0,
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

    def insert(self, marking_ype, *args):
        pass

    def insert_volta_bracket(self):
        pass

    def insert_tempo(self):
        pass

    def insert_dynamic(self):
        pass

    def has_ls_barline(self) -> bool:
        """
        Describes if the measure has any left-sided barlines

        :return: If this measure has any left-sided barlines
        """
        # If there are a list of barlines
        if isinstance(self.barline, list):

            for bl in self.barline:
                if isinstance(bl, Barline):
                    if bl.barlinelocation == BarlineLocation.LEFT:
                        return True

            return False

        # Otherwise, if the only barline here is left-sided
        elif isinstance(self.barline, Barline):
            return self.barline.barlinelocation == BarlineLocation.LEFT

        else:
            return False

    def has_irregular_rs_barline(self) -> bool:
        """
        Describes if the measure has a right-sided barline that isn't regular

        :return: If this measure has a right-sided barline that isn't regular
        """
        # If there are a list of barlines
        if isinstance(self.barline, list):

            for bl in self.barline:
                if isinstance(bl, Barline):
                    if bl.barlinelocation == BarlineLocation.RIGHT and bl.barlinetype != BarlineType.REGULAR:
                        return True

            return False

        elif isinstance(self.barline, Barline):
            if self.barline.barlinelocation == BarlineLocation.RIGHT:
                return self.barline.barlinetype != BarlineType.REGULAR

            else:
                return False

        elif isinstance(self.barline, BarlineType):
            return self.barline != BarlineType.REGULAR

        else:
            raise TypeError(
                f'Measure {self} has a barline of invalid type {type(self.barline)}.')

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def empty_measure(cls) -> 'Measure':
        """
        Used for keeping track of when a measure has unset elements in mxml.py

        :return:
        """
        empty_measure = Measure()
        empty_measure.key = None
        empty_measure.time = None
        empty_measure.clef = None
        empty_measure.divisions = None
        empty_measure.transposition = None
        return empty_measure

    @classmethod
    def from_abc(cls):
        pass
