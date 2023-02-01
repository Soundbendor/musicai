from enum import Enum, auto

import pyglet
import json

from structure.measure import Barline, BarlineLocation, BarlineType
from structure.note import NoteGroup, Rest, Note
from structure.pitch import Pitch
from pyglet import shapes
from visualization.window_config import WindowConfig

_DEBUG = False

# stores [[sharps], [flats], [double sharp], [double flat]]
# TODO: modes
key_accidentals = {
    # major scales
    1: [[], []],
    2: [['F'], []],
    3: [['F', 'C'], []],
    4: [['F', 'C', 'G'], []],
    5: [['F', 'C', 'G', 'D'], []],
    6: [['F', 'C', 'G', 'D', 'A'], []],
    7: [['F', 'C', 'G', 'D', 'A', 'E'], []],
    8: [['F', 'C', 'G', 'D', 'A', 'E', 'B'], []],
    9: [[], ['B']],
    10: [[], ['B', 'E']],
    11: [[], ['B', 'E', 'A']],
    12: [[], ['B', 'E', 'A', 'D']],
    13: [[], ['B', 'E', 'A', 'D', 'G']],
    14: [[], ['B', 'E', 'A', 'D', 'G', 'C']],
    15: [[], ['B', 'E', 'A', 'D', 'G', 'C', 'F']]
}


class GlyphType(Enum):
    CLEF = auto()
    TIME = auto()
    KEY = auto()
    NOTE_UP = auto()
    NOTE_DOWN = auto()
    REST = auto()
    ACCIDENTAL = auto()
    LEGER = auto()
    BARLINE = auto()

    # -----------
    # Constructor
    # -----------

    def __new__(cls, *values):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        return obj


class Glyph(pyglet.text.Label):
    glyph_map = json.load(open('./visualization/assets/glyphnames.json'))

    def __init__(self, gtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_x = self.x
        self.label_y = self.y
        self.gtype = gtype

    @classmethod
    def code(cls, glyph_id):
        if glyph_id in cls.glyph_map:
            code_str = cls.glyph_map[glyph_id]['codepoint']
            return chr(int(code_str[2:], 16))
        else:
            print("Not found: " + glyph_id)
            raise ValueError('Glyph {0} not found in font.'.format(glyph_id))

    def __str__(self):
        return f"x: {self.label_x:.3f} y: {self.label_y:.3f} glyph type: {self.gtype}"

    def __repr__(self):
        return self.__str__()


class ViewArea():

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.labels = []
        self.msvcfg = WindowConfig()

    def layout(self):
        pass

    def draw(self):
        pass


class MeasureArea(ViewArea):

    def __init__(self, measure, x=0, y=0, height=80, key_sig_width=0, idx=0, width=0):
        super().__init__(x, y)
        self.measure = measure
        self.area_x = x             # Used to store the initial value of x and y as loaded in
        self.area_y = y
        # Used to store the total width and height a measure takes up
        self.area_width = width
        self.area_height = height
        self.spacing = self.area_height // 4
        self.batch = pyglet.graphics.Batch()
        self.barlines = []
        self.irr_barlines = []
        self.irr_barlines_idx = []
        self.ledger_lines = []
        self.index = idx
        self.key_sig_width = key_sig_width
        self.layout()

    def layout(self):
        if _DEBUG:
            print('========')
            print('measure=', self.measure.measure_number, self.measure)

        x = self.area_x
        y = self.area_y

        clef_pitch = self._clef_line_pitch()

        if self.index == 0:
            x, y = self.layout_left_barline(x, y)
        else:
            x += 24

        # x, y = self.layout_left_barline(x,y)
        x, y = self.layout_clef(x, y)
        x, y = self.layout_key_signature(x, y)
        x, y = self.layout_time_signature(x, y)
        for note in self.measure.notes:
            x, y, = self.layout_notes(note, clef_pitch, x=x, y=y)

        if (self.area_width != 0):
            x = self.area_width + self.area_x
        x, y = self.layout_right_barline(x, y)

        self.area_width = x - self.area_x
        self.area_height = y + 36

    def _clef_line_pitch(self):
        clef_value = self.measure.clef.value
        line_offset = 3 - self.measure.clef.line
        clef_pitch = self.measure.clef.value + line_offset * 2
        if _DEBUG:
            print('clef_value=', clef_value,
                  self.measure.clef.line, line_offset, clef_pitch)
        return clef_pitch

    # use c4 as 0
    def note_offset(self, note):
        step = note.pitch.step.name
        octave = note.pitch.octave
        offset = 0

        match step:
            case 'C':
                offset += 0
            case 'D':
                offset += 1
            case 'E':
                offset += 2
            case 'F':
                offset += 3
            case 'G':
                offset += 4
            case 'A':
                offset += 5
            case 'B':
                offset += 6

        octave_offset = (int(octave) - 4) * 7
        offset += octave_offset

        # TODO offset for different clefs (tenor clef + more uncommon)
        clef_pitch = self.measure.clef.value
        clef_offset = 0
        match clef_pitch:
            case 53:  # bass clef
                clef_offset = 12
            case 60:  # alto clef
                clef_offset = 6
        if _DEBUG:
            print('clef_pitch' + str(clef_pitch))
        offset += clef_offset
        return offset

    def layout_notes(self, note, clef_pitch, x, y):
        # TODO replace constant 10 with (staff) spacing // 2
        if isinstance(note, Rest):
            if _DEBUG:
                print('rest=', note, note.glyph)
            rest_label = self.add_label(
                note.glyph, GlyphType.REST, x=x, y=y + (self.spacing // 2) * 6 + 15)
            # Replace six with env['HSPACE'] or equivalent solution
            x += rest_label.content_width + int((6 * (100 * note.value))) * float(note.value) * 15
            return x, y

        notes = []
        if isinstance(note, NoteGroup):
            # unpack notes in chord
            # TODO attach beams in between the notes
            if _DEBUG:
                print('note_group=', note.is_note_group(), note, note.pitch)
            notes.extend(note.notes)
        elif isinstance(note, Note):
            # single note
            notes.append(note)

        for n in notes:
            # print(str(n.pitch.step.name) + str(n.pitch.octave) +
            #       ' ' + str(n.pitch.midi))
            # (n.pitch.midi - clef_pitch)//2
            line_offset = self.note_offset(note)
            # accidentals
            if str(n.accidental).strip() != '':
                if n.pitch.step not in self.measure.key.altered():
                    accidental_label = self.add_label(
                        n.accidental.glyph, GlyphType.ACCIDENTAL, x, y + 3 + (line_offset + 1) * (self.spacing // 2))  # (+ 3) to align glyph with staff
                    x += accidental_label.content_width + 6
            # notes
            if str(n.stem) == 'StemType.UP':    # Need to find better way not using str()
                gtype = GlyphType.NOTE_UP
            else: 
                gtype = GlyphType.NOTE_DOWN
            # Replace 6 with env['VSPACE'] or equivalent solution
            note_label = self.add_label(
                n.glyph, gtype, x=x, y=y + 3 + (line_offset + 1) * (self.spacing // 2))  # (+ 3) to align glyph with staff

            # ledger lines
            self.layout_ledger_lines(
                x, y, line_offset)

            # x offset for notes
            x += note_label.content_width + int((6 * (100 * n.value))) * float(n.value) * 15
        return x, y

    def layout_left_barline(self, x, y):
        # only if Barline is on left
        if _DEBUG:
            print('l-barline=', self.measure.barline)
        if isinstance(self.measure.barline, Barline):
            barline_label = self.add_label(
                self.measure.barline.barlinetype.glyph, GlyphType.BARLINE, x=x, y=y + (self.area_height//2))
            x += 18 + barline_label.content_width
        elif isinstance(self.measure.barline, BarlineType):
            barline_verts = []
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x)
            barline_verts.append(y + self.area_height)
            self.barlines.append(barline_verts)
            x += 18
        return x, y

    def layout_right_barline(self, x, y):
        if isinstance(self.measure.barline, Barline):
            barline_label = self.add_label(
                self.measure.barline.barlinetype.glyph, GlyphType.BARLINE, x=x, y=y + (self.area_height//2))
            barline_verts = []
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x + barline_label.content_width)
            barline_verts.append(y + self.area_height)
            self.irr_barlines.append(barline_verts)
            self.irr_barlines_idx.append(self.index)
            x += 18 + barline_label.content_width
        elif isinstance(self.measure.barline, BarlineType):
            barline_verts = []
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x)
            barline_verts.append(y + self.area_height)
            self.barlines.append(barline_verts)
            x += 18
        return x, y

    def layout_clef(self, x, y):
        if (self.index == 0):
            x += 12
            clef_pitch = self.measure.clef.value
            # base is treble (G) clef
            clef_offset = self.spacing // 2 + 10
            match clef_pitch:
                case 53:  # bass clef
                    clef_offset = (self.spacing // 2) * 5 + 10
                case 60:  # alto clef
                    clef_offset = (self.spacing // 2) * 3 + 10
            clef_label = self.add_label(
                self.measure.clef.glyph, GlyphType.CLEF, x=x, y=y + self.spacing * 2 + clef_offset)
            x += clef_label.content_width + 10
        return x, y

    def layout_time_signature(self, x, y):
        if (self.index == 0):
            time_sig = self.measure.time
            # time_sig_numerator = pyglet.text.Label(str(time_sig.numerator),
            #                                        font_name=self.msvcfg.MUSIC_FONT_NAME,
            #                                        font_size=int(
            #                                            self.msvcfg.MUSIC_FONT_SIZE - 5),
            #                                        x=x, y=y + self.spacing * 3 + 8,
            #                                        anchor_x='center', anchor_y='center')
            numerator_glyph = 'timeSig' + str(time_sig.numerator)
            time_sig_numerator = self.add_label(
                numerator_glyph, GlyphType.TIME, x, y=y + self.spacing * 4.5)
            denominator_glyph = 'timeSig' + str(time_sig.denominator)
            # time_sig_denominator = pyglet.text.Label(str(time_sig.denominator),
            #                                          font_name=self.msvcfg.MUSIC_FONT_NAME,
            #                                          font_size=int(
            #                                              self.msvcfg.MUSIC_FONT_SIZE - 5),
            #                                          x=x, y=y + self.spacing + 10,
            #                                          anchor_x='center', anchor_y='center')
            time_sig_denominator = self.add_label(
                denominator_glyph, GlyphType.TIME, x, y=y + self.spacing * 2.5)

            x += time_sig_numerator.content_width + 15

        return x, y

    def key_sig_accidental_offset(self, note, accidental_type):
        offset = 0

        match note:
            case 'C':
                offset += 8
            case 'D':
                offset += 9
            case 'E':
                offset += 10
            case 'F':
                if (accidental_type == 'sharp'):
                    offset += 11
                else:
                    offset += 3
            case 'G':
                if (accidental_type == 'sharp'):
                    offset += 12
                else:
                    offset += 4
            case 'A':
                offset += 5
            case 'B':
                offset += 6

        return offset

    def lookup_key_accidentals(self, key):
        accidentals = [[], []]
        match key:
            case 'C Major' | 'A Minor':
                accidentals = key_accidentals[1]
            case 'G Major' | 'E Minor':
                accidentals = key_accidentals[2]
            case 'D Major' | 'B Minor':
                accidentals = key_accidentals[3]
            case 'A Major' | 'Fs Minor':
                accidentals = key_accidentals[4]
            case 'E Major' | 'Cs Minor':
                accidentals = key_accidentals[5]
            case 'B Major' | 'Gs Minor':
                accidentals = key_accidentals[6]
            case 'Fs Major' | 'Ds Minor':
                accidentals = key_accidentals[7]
            case 'Cs Major' | 'As Minor':
                accidentals = key_accidentals[8]
            case 'F Major' | 'D Minor':
                accidentals = key_accidentals[9]
            case 'Bb Major' | 'G Minor':
                accidentals = key_accidentals[10]
            case 'Eb Major' | 'C Minor':
                accidentals = key_accidentals[11]
            case 'Ab Major' | 'F Minor':
                accidentals = key_accidentals[12]
            case 'Db Major' | 'Bb Minor':
                accidentals = key_accidentals[13]
            case 'Gb Major' | 'Eb Minor':
                accidentals = key_accidentals[14]
            case 'Cb Major' | 'Ab Minor':
                accidentals = key_accidentals[15]
        return accidentals

    def layout_key_signature(self, x, y):
        if (self.index == 0):
            key = self.measure.key
            accidentals = self.lookup_key_accidentals(key.__str__())
            if _DEBUG:
                print(key_accidentals[key.__str__()])
            if len(accidentals[0]) == 0 and len(accidentals[1]) == 0:
                accidental_label = self.add_label(
                    'accidentalFlat', GlyphType.ACCIDENTAL, x, y)
                # pass
                x += (accidental_label.content_width + 4) * self.key_sig_width
                self.labels.pop()
            else:
                for note in accidentals[0]:
                    line_offset = self.key_sig_accidental_offset(note, 'sharp')
                    accidental_label = self.add_label(
                        'accidentalSharp', GlyphType.ACCIDENTAL, x, y + 3 + (line_offset) * (self.spacing // 2))  # (+ 3) to align glyph with staff
                    x += accidental_label.content_width + 4
                for note in accidentals[1]:
                    line_offset = self.key_sig_accidental_offset(note, 'flat')
                    accidental_label = self.add_label(
                        'accidentalFlat', GlyphType.ACCIDENTAL, x, y + 3 + (line_offset) * (self.spacing // 2))  # (+ 3) to align glyph with staff
                    x += accidental_label.content_width + 4
        x += 10
        return x, y

    def layout_ledger_lines(self, x, y, line_offset):
        if (line_offset < 3):
            for num in range(line_offset - 1, 3):
                if num % 2 != 0:
                    ledger_line_verts = []
                    ledger_line_verts.append(x - (self.spacing) - 4)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    ledger_line_verts.append(x + (self.spacing) - 4)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    self.ledger_lines.append(ledger_line_verts)

        elif (line_offset > 11):
            for num in range(11, line_offset):
                if num % 2 != 0:
                    ledger_line_verts = []
                    ledger_line_verts.append(x - (self.spacing) + 2)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    ledger_line_verts.append(x + (self.spacing) + 2)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    self.ledger_lines.append(ledger_line_verts)

    def draw(self):
        for label in self.labels:
            label.draw()

    def add_label(self, glyph, gtype, x=0, y=0):
        glyph_id = Glyph.code(glyph)
        font_size = self.msvcfg.MUSIC_FONT_SIZE
        note_off = 0

        # if gtype == GlyphType.NOTE_UP:  # Possibly move this elsewear (parameter)
        #     note_off = 20

        if gtype == GlyphType.CLEF: # Possibly make font size a parameter
            font_size = self.msvcfg.MUSIC_CLEF_FONT_SIZE
        
        label = Glyph(gtype=gtype,
                      text=glyph_id,
                      font_name=self.msvcfg.MUSIC_FONT_NAME,
                      font_size=int(font_size),
                      x=x + note_off, y=y,
                      anchor_x='center',
                      anchor_y='center')
        label.color = (0, 0, 0, 255)
        self.labels.append(label)
        return label

    def get_labels(self):
        return self.labels

    def get_barlines(self):
        return self.barlines

    def get_irr_barlines(self):
        return self.irr_barlines

    def get_irr_barlines_idx(self):
        return self.irr_barlines_idx

    def get_ledger_lines(self):
        return self.ledger_lines
