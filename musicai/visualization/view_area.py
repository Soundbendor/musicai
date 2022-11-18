from enum import Enum, auto

import pyglet
import json

from structure.measure import Barline, BarlineLocation, BarlineType
from structure.note import NoteGroup, Rest, Note
from structure.pitch import Pitch

# TODO Figure out if build_env is best practice for python and change magic numbers to what's commented

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


class Glyph(pyglet.text.Label): #normally takes arcade.text as param find out why? --- maybe do pyglet.text.Label instead(?)
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

class ViewArea():

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.labels = []

    def layout(self):
        pass

    def draw(self):
        pass


class MeasureArea(ViewArea):

    def __init__(self, measure, x=0, y=0):
        super().__init__(x,y)
        self.measure = measure
        self.area_x = x             # Used to store the initial value of x and y as loaded in
        self.area_y = y
        self.area_width = x         # Used to store the total width and height a measure takes up
        self.area_height = y
        self.layout()
    
    def layout(self):
        print('========')
        print('measure=', self.measure.measure_number, self.measure)
        x = self.area_x
        y = self.area_y

        clef_pitch = self._clef_line_pitch()
        
        x, y =  self.layout_left_barline(x, y)      # TODO left barline should only print for first measure otherwise print right barline
        for note in self.measure.notes:
            x, y, = self.layout_notes(note, clef_pitch, x=x, y=y)

        # Currently not setting right barline and instead just setting left one

        self.area_width = x - self.area_x
        self.area_height = y + 36

    def _clef_line_pitch(self):
        clef_value = self.measure.clef.value
        line_offset = 3 - self.measure.clef.line
        clef_pitch = self.measure.clef.value + line_offset * 2
        print('clef_value=', clef_value, self.measure.clef.line, line_offset, clef_pitch)
        return clef_pitch

    def layout_notes(self, note, clef_pitch, x, y):
        if isinstance(note, Rest):
            print('rest=', note, note.glyph)
            rest_label = self.add_label(note.glyph, GlyphType.REST, x=x, y=y)
            x += rest_label.content_width + 6                                   # Replace six with env['HSPACE'] or equivalent solution
            return x, y
        
        notes = []
        if isinstance(note, NoteGroup):
            # unpack notes in chord 
            # TODO attach beams in between the notes
            print('note_group=', note.is_note_group(), note, note.pitch)
            notes.extend(note.notes)
        elif isinstance(note, Note):
            # single note
            notes.append(note)

        for n in notes:
            line_offset = (n.pitch.midi - clef_pitch)//2
            if str(n.accidental).strip() != '':
                if n.pitch.step not in self.measure.key.altered():
                    accidental_label = self.add_label (n.accidental.glyph, GlyphType.ACCIDENTAL, x, y + 6 * line_offset)
                    x += accidental_label.content_width + 6                           # Replace 6 with env['HSPACE'] or equivalent solution

            gtype = GlyphType.NOTE_UP if n.stem.UP else GlyphType.NOTE_DOWN
            note_label = self.add_label(n.glyph, gtype, x=x, y=y + (line_offset * 6)) # Replace 6 with env['VSPACE'] or equivalent solution
            x += note_label.content_width + int((6 * (100 * n.value)))                # Replace 6 with env['HSPACE'] or equivalent solution
        return x,y

    def layout_left_barline(self, x, y):
        # only if Barline is on left

        print('l-barline=', self.measure.barline)
        if isinstance(self.measure.barline, BarlineType):
            barline_label = self.add_label(self.measure.barline.glyph, GlyphType.BARLINE, x=x, y=y - 4 *6)      # Replace 6 with env['VSPACE'] or equivalent solution
            x += barline_label.content_width + 6 * 2                                                            # Replace 6 with env['HSPACE'] or equivalent solution
        return x, y

    def draw(self):
        for label in self.labels:
            label.draw()
    
    def add_label(self, glyph, gtype, x=0, y=0):
        glyph_id = Glyph.code(glyph)
        label = Glyph(gtype=gtype,
                      text=glyph_id,
                      font_name='Bravura',
                      font_size=36,
                      x=x,y=y,
                      anchor_x='center',
                      anchor_y='center')
        label.color = (0,0,0,255)
        self.labels.append(label)
        return label