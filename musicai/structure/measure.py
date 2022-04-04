import re
from enum import Enum

from musicai.structure.note_mark import StemType
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

    def __str__(self):
        return self.symbol


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
    def __init__(self, barlinetype=BarlineType.REGULAR, barlinelocation=BarlineLocation.RIGHT):
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
            raise ValueError('Cannot match abc string \'{0}\' to a Barline'.format(abc_barline))
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
        self.barline = BarlineType.REGULAR
        self.is_full = False
        self.remaining = 1.0
        self.display_clef = False
        self.display_time = False
        self.display_key = False
        self.measure_style = MeasureStyle.NONE

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for note in self.notes:
            if note is None:
                raise ValueError('note is None')
            ret_str += ' ' + str(note)
        ret_str += ' ' + str(self.barline)
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
            raise TypeError('Cannot add type {0} to Measure'.format(type(notes)))
        self.pack()

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

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls):
        pass
