from __future__ import annotations
from enum import Enum, auto

import pyglet
import json

from structure.measure import Barline, BarlineLocation, BarlineType
from structure.measure_mark import DynamicMark, DynamicType, DynamicChangeType
from structure.note import NoteGroup, Rest, Note, DotType
from structure.score import PartSystem
from visualization.window_config import WindowConfig
from pyglet.shapes import Line

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
    DOT = auto()

    # -----------
    # Constructor
    # -----------

    def __new__(cls, *values):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        return obj


class Glyph(pyglet.text.Label):
    _glyph_map = json.load(open('./visualization/assets/glyphnames.json'))

    def __init__(self, glyph, gtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_x = self.x
        self.label_y = self.y
        self.gtype = gtype
        self.font_size = self._font_size(glyph)

    @classmethod
    def code(cls, glyph_id):
        if glyph_id in cls._glyph_map:
            code_str = cls._glyph_map[glyph_id]['codepoint']
            return chr(int(code_str[2:], 16))
        else:
            print("Not found: " + glyph_id)
            raise ValueError('Glyph {0} not found in font.'.format(glyph_id))

    def _font_size(self, glyph):
        match self.gtype:  # Possibly make these parameters
            case GlyphType.CLEF:
                font_size = WindowConfig().MUSIC_CLEF_FONT_SIZE
            case GlyphType.TIME:
                font_size = WindowConfig().MUSIC_TIME_SIG_FONT_SIZE
            case GlyphType.ACCIDENTAL:
                font_size = WindowConfig().MUSIC_ACC_FONT_SIZE
            case _:
                font_size = WindowConfig().MUSIC_FONT_SIZE

        if glyph == 'noteheadBlack':
            font_size = WindowConfig().MUSIC_NB_FONT_SIZE

        return font_size

    def __str__(self):
        return f"x: {self.label_x:.3f} y: {self.label_y:.3f} glyph type: {self.gtype}"

    def __repr__(self):
        return self.__str__()


class Staff:
    # TODO Instead of so many parameters, maybe create a new class for StaffParams or something like it?
    def __init__(self, num_parts: int = 0, measure_widths: list[int] = None,
                 staff_lines: int = 5, height: int = 0, batch: pyglet.graphics.Batch = None) -> None:

        # TODO Should we do some type of validation on parameters here?
        self._lines = self._part_staff_lines(
            num_parts, measure_widths, height, staff_lines, batch)

    @staticmethod
    def _measure_staff_lines(x_start, y_start, staff_length, staff_lines, batch):
        barlines = list()

        for val in range(staff_lines):
            y_value = y_start + val * \
                (WindowConfig().MEASURE_LINE_SPACING * WindowConfig().ZOOM)
            x_end = (x_start + staff_length) * WindowConfig().ZOOM
            barlines.append(Line(
                x_start, y_value, x_end, y_value, width=2, color=(0, 0, 0), batch=batch))

        return barlines

    def _part_staff_lines(self, num_parts, measure_widths, height, staff_lines, batch):
        lines = list()

        for part_idx in range(num_parts):
            total_width = 0

            for width in measure_widths:
                measure_length = height - WindowConfig().TOP_OFFSET - \
                    (part_idx * WindowConfig().MEASURE_OFFSET)

                lines.extend(Staff._measure_staff_lines(x_start=total_width, y_start=measure_length, staff_length=width,
                                                        staff_lines=staff_lines, batch=batch))

                total_width += width

        return lines

    def staff_lines(self):
        return self._lines


class LedgerLine:
    def __init__(self, ledger_coords: list[int] = None, batch: pyglet.graphics.Batch = None) -> None:
        self._lines = self._draw(ledger_coords, batch)

    def _draw(self, ledger_coords, batch):
        ledger_lines = list()
        for coords in ledger_coords:
            ledger_line = Line(
                coords[0], coords[1], coords[2], coords[3], width=2, color=(0, 0, 0), batch=batch)
            ledger_lines.append(ledger_line)

        return ledger_lines

    def ledger_lines(self):
        return self._lines


class PartDisplay:
    def __init__(self):
        self.measures = None


class MeasureDisplay:
    def __init__(self, batch: pyglet.graphics.Batch = None) -> None:
        self.batch = batch
        self.clef = None


class ClefMeasure:
    def __init__(self, clef) -> None:
        self.clef = clef


class MeasureArea:
    def __init__(self, measure, x=0, y=0, height=80, key_sig_width=0, idx=0, width=0, config=None, batch=None):
        self._cfg = config
        self.labels = []
        self.measure = measure
        self.area_x = x             # Used to store the initial value of x and y as loaded in
        self.area_y = y
        # Used to store the total width and height a measure takes up
        self.area_width = width
        self.area_height = height
        self.spacing = self.area_height // 4
        self.batch = batch
        self.barlines = []
        self.irr_barlines = []
        self.irr_barline_labels = []
        self.ledger_lines = []
        self.hairpin_start = []
        self.hairpin_end = []
        self.index = idx
        self.key_sig_width = key_sig_width
        self.beam_lines = []
        self.stems = []
        self.layout()

    def layout(self):
        if _DEBUG:
            print('========')
            print('measure=', self.index, self.measure)

        x = self.area_x
        y = self.area_y

        if self.index == 0:
            x, y = self.layout_left_barline(x, y)
        else:
            x += 24

        # x, y = self.layout_left_barline(x,y)
        x, y = self.layout_clef(x, y)
        x, y = self.layout_key_signature(x, y)
        x, y = self.layout_time_signature(x, y)
        beam_notes = []
        note_idx = 0
        for note in self.measure.notes:
            if len(note.beams) == 0:
                # self.layout_right_barline(x, y)
                if not isinstance(note, Rest) or note_idx == 1:
                    note_idx += 1
                if note_idx == 1:
                    self.layout_dynamic_markings(x, y-30)
                x, y, = self.layout_notes(note, x=x, y=y)
            else:
                x, y, beam_notes = self.layout_beamed_notes(
                    note, beam_notes, x=x, y=y)

        x, y = self.layout_right_barline(x, y)

        self.area_width = x - self.area_x
        self.area_height = y + 36

    # use c4 as 0
    def note_offset(self, note: Note) -> int:
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
        match clef_pitch:
            case 53:  # bass clef
                clef_offset = 12
            case 60:  # alto clef
                clef_offset = 6
            case _:
                clef_offset = 0
        if _DEBUG:
            print('clef_pitch' + str(clef_pitch))
        offset += clef_offset
        return offset

    @staticmethod
    def get_notehead(note: Note) -> str:
        if note.glyph == 'noteHalfDown' or note.glyph == 'noteHalfUp':
            return 'noteheadHalf'
        else:
            return 'noteheadBlack'

    def layout_beamed_notes(self, note: Note, beam_notes: list, x: int, y: int) -> tuple:
        # collect beamed notes in one list
        beam_notes = beam_notes  # list of tuples ((x_pos, y_pos), Note)

        layout_beam = False
        # layout noteheads
        if note.beams[0].beamtype.value == 1:
            beam_notes = []
        elif note.beams[0].beamtype.value == 3:
            layout_beam = True

        notes = []
        if isinstance(note, NoteGroup):
            # unpack notes in chord
            if _DEBUG:
                print('note_group=', note.is_note_group(), note, note.pitch)
            notes.extend(note.notes)
        elif isinstance(note, Note):
            # single note
            notes.append(note)

        for n in notes:
            line_offset = self.note_offset(note)
            # note satellites
            self.layout_satellites(x, y, line_offset, n)

            if str(n.stem) == 'StemType.UP':    # Need to find better way not using str()
                gtype = GlyphType.NOTE_UP
            else:
                gtype = GlyphType.NOTE_DOWN

            notehead = self.get_notehead(n)

            self.add_label(
                notehead, gtype, x=x, y=y + 8 + (line_offset + 1) * (self.spacing // 2))  # (+ 3) to align glyph with
            # staff

            beam_notes.append(
                ((x - 2, y + (line_offset - 2) * (self.spacing // 2)), note))

            # ledger lines
            self.layout_ledger_lines(
                x, y, line_offset, note)

            # x offset for notes
            x += self._cfg.NOTE_WIDTH * float(note.value) * 20
            # x += note_label.content_width + \
            #     int((6 * (100 * n.value))) * float(n.value) * 15

        # layout beams and stems
        if layout_beam:
            if _DEBUG:
                for note in beam_notes:
                    print(note[1].value, note[1].beams[0], note[1].stem)

            # get beam direction
            beam_direction = 0
            for n_tuple in beam_notes:
                beam_direction = n_tuple[1].stem.value
                if n_tuple[1].stem.value != beam_direction:
                    beam_direction = 3
                    break
            # beam algo params
            x_offset = None
            stem_direction = None
            # all up stem
            if beam_direction == 1:
                beam_type = 1
                x_offset = 12
                stem_direction = 1
            # all down stem
            elif beam_direction == -1:
                beam_type = 1
                x_offset = -7
                stem_direction = -1
            else:
                beam_type = 2

            # all up / down stems
            if beam_type == 1:
                # calc slope
                slope_y = beam_notes[-1][0][1] - beam_notes[0][0][1]
                slope_x = beam_notes[-1][0][0] - beam_notes[0][0][0]
                slope = 0
                if slope_x != 0:
                    slope = slope_y / slope_x
                # max / min slope is 0.35 / - 0.35, adjust if necessary
                if slope > 0.35 or slope < -0.35:
                    if slope < 0:
                        slope = -0.35
                    else:
                        slope = 0.35
                if _DEBUG:
                    print('Slope: ', slope)

                # TODO: make dynamic for zooming
                # calculate y for stem tip
                y_0 = 0
                if stem_direction == 1:
                    index = 0
                    max_y = float('-inf')
                    for idx, n_tuple in enumerate(beam_notes):
                        if n_tuple[0][1] > max_y:
                            max_y = n_tuple[0][1]
                            index = idx
                    max_y += self.spacing * 2
                    y_0 = max_y - slope * index
                elif stem_direction == -1:
                    index = 0
                    min_y = float('inf')
                    for idx, n_tuple in enumerate(beam_notes):
                        if n_tuple[0][1] < min_y:
                            min_y = n_tuple[0][1]
                            index = idx
                    min_y -= self.spacing * 2
                    y_0 = min_y - slope * index

                # layout beams
                beam_nums = []  # list of number of beams for note value at index
                for idx, n_tuple in enumerate(beam_notes):
                    # add base stem
                    stem_base = (n_tuple[0][0] + x_offset, n_tuple[0]
                                 [1])
                    stem_tip = (n_tuple[0][0] + x_offset,
                                n_tuple[0][1] + slope * idx + (y_0 - n_tuple[0][1]))
                    self.stems.append(
                        [stem_base[0], stem_base[1], stem_tip[0], stem_tip[1]])

                    # use glyph to get number of beams for note
                    beam_num = 0
                    # eighth note
                    if str(n_tuple[1].glyph) == 'note8thDown' or str(n_tuple[1].glyph) == 'note8thUp':
                        beam_num = 1
                    # 16th note
                    if str(n_tuple[1].glyph) == 'note16thDown' or str(n_tuple[1].glyph) == 'note16thUp':
                        beam_num = 2
                    # 32nd note
                    if str(n_tuple[1].glyph) == 'note32ndDown' or str(n_tuple[1].glyph) == 'note32ndUp':
                        beam_num = 3
                    # 64th note
                    if str(n_tuple[1].glyph) == 'note64thDown' or str(n_tuple[1].glyph) == 'note64thUp':
                        beam_num = 4
                    if str(n_tuple[1].glyph) == 'note128thDown' or str(n_tuple[1].glyph) == 'note128thUp':
                        beam_num = 5
                    if str(n_tuple[1].glyph) == 'note256thDown' or str(n_tuple[1].glyph) == 'note256thUp':
                        beam_num = 6
                    if str(n_tuple[1].glyph) == 'note512thDown' or str(n_tuple[1].glyph) == 'note512thUp':
                        beam_num = 7
                    if str(n_tuple[1].glyph) == 'note1024thDown' or str(n_tuple[1].glyph) == 'note1024thUp':
                        beam_num = 8
                    beam_nums.append(beam_num)

                for i in range(len(beam_nums)):
                    adjust_idx = 0
                    if len(beam_nums) < len(self.stems):
                        adjust_idx = len(self.stems) - len(beam_nums)
                    # base bar y (lowest / highest bar)
                    base_y_offset = (max(beam_nums) - 1) * \
                        stem_direction * (self.spacing // 2) + 4
                    # adjust for beam line width
                    if stem_direction == 1:
                        base_y_offset -= 8
                    # add half beam forward and half beam backward for note
                    if i == 0:
                        # add backward half beam
                        back_beam_dist = (
                            self.stems[adjust_idx + 1][0] - self.stems[adjust_idx][0]) / 2
                        for j in range(beam_nums[0] - 1, -1, -1):
                            self.beam_lines.append([self.stems[adjust_idx][2], self.stems[adjust_idx][3] + base_y_offset + j *
                                                    self.spacing // 2 * (stem_direction * -1),
                                                    self.stems[adjust_idx][2] + back_beam_dist, self.stems[adjust_idx][3] +
                                                    base_y_offset + j * self.spacing // 2 * (stem_direction * -1)])
                    elif i == len(beam_nums) - 1:
                        # add forward half beam
                        forward_beam_dist = (self.stems[adjust_idx + i][0] -
                                             self.stems[adjust_idx + i - 1][0]) / 2
                        for j in range(beam_nums[i] - 1, -1, -1):
                            self.beam_lines.append([
                                self.stems[adjust_idx + i][2],
                                self.stems[adjust_idx + i][3] + base_y_offset + j * (self.spacing // 2) * (stem_direction * -1),
                                self.stems[adjust_idx + i][2] - forward_beam_dist - 2,
                                self.stems[adjust_idx + i][3] + base_y_offset + j * (self.spacing // 2) * (stem_direction * -1)])
                    else:
                        # add forward and backward half beams
                        back_beam_dist = (
                            self.stems[adjust_idx + i + 1][0] - self.stems[adjust_idx + i][0]) / 2
                        for j in range(beam_nums[i + 1] - 1, -1, -1):
                            self.beam_lines.append([self.stems[adjust_idx + i][2],
                                                    self.stems[adjust_idx + i][3] + base_y_offset + j * self.spacing // 2 * (stem_direction * -1),
                                                    self.stems[adjust_idx + i][2] + back_beam_dist + 1,
                                                    self.stems[adjust_idx + i][3] + base_y_offset + j * self.spacing // 2 * (stem_direction * -1)])
                        forward_beam_dist = (self.stems[adjust_idx + i][0] -
                                             self.stems[adjust_idx + i - 1][0]) / 2
                        for j in range(beam_nums[i - 1] - 1, -1, -1):
                            self.beam_lines.append([
                                self.stems[adjust_idx + i][2],
                                self.stems[adjust_idx + i][3] + base_y_offset + j * (self.spacing // 2) * (stem_direction * -1),
                                self.stems[adjust_idx + i][2] - forward_beam_dist - 1,
                                self.stems[adjust_idx + i][3] + base_y_offset + j * (self.spacing // 2) * (stem_direction * -1)])

                # adjust stems to match base bar y
                for i in range(len(self.stems) - len(beam_nums), len(self.stems)):
                    self.stems[i][3] += (max(beam_nums) - 1) * \
                        stem_direction * (self.spacing // 2)
            # TODO split stem
            elif beam_direction == 3:
                pass

        return x, y, beam_notes

    def layout_notes(self, note, x, y):
        # TODO replace constant 10 with (staff) spacing // 2
        if isinstance(note, Rest):
            if _DEBUG:
                barline_verts = list()
                barline_verts.append(x)
                barline_verts.append(y)
                barline_verts.append(x)
                barline_verts.append(y + self.area_height)
                self.barlines.append(barline_verts)
            if _DEBUG:
                print('rest=', note, note.glyph)
            self.add_label(
                note.glyph, GlyphType.REST, x=x, y=y + (self.spacing // 2) * 6 + 15)  # (+15) glyph alignment
            # Replace six with env['HSPACE'] or equivalent solution
            # x += rest_label.content_width + int((6 * (100 * note.value))) * float(note.value) * 15
            x += self._cfg.NOTE_WIDTH * float(note.value) * 20
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
            if _DEBUG:
                barline_verts = list()
                barline_verts.append(x)
                barline_verts.append(y)
                barline_verts.append(x)
                barline_verts.append(y + self.area_height)
                self.barlines.append(barline_verts)
            line_offset = self.note_offset(note)
            # note satellites
            self.layout_satellites(x, y, line_offset, n)
            # notes
            if str(n.stem) == 'StemType.UP':    # Need to find better way not using str()
                gtype = GlyphType.NOTE_UP
            else:
                gtype = GlyphType.NOTE_DOWN
            self.add_label(
                n.glyph, gtype, x=x, y=y + 3 + (line_offset + 1) * (self.spacing // 2))  # (+ 3) to align glyph with
            # staff

            # ledger lines
            self.layout_ledger_lines(
                x, y, line_offset, note)

            # x offset for notes
            # x += note_label.content_width + int((6 * (100 * n.value))) * float(n.value) * 15
            x += self._cfg.NOTE_WIDTH * float(note.value) * 20
        return x, y

    def layout_satellites(self, x: int, y: int, line_offset: int, note: Note):
        # accidentals
        if str(note.accidental).strip() != '':
            if note.pitch.step not in self.measure.key.altered():
                self.layout_accidental(
                    x, y, line_offset, note.accidental.glyph)
        # dots
        if note.value.dots != DotType.NONE:
            self.layout_dots(x, y, line_offset, note.value.dots.value)

    def layout_dots(self, x: int, y: int, line_offset: int, num_dots: int):
        for i in range(1, 1 + num_dots):
            self.add_label(
                'augmentationDot', GlyphType.DOT, x + self.spacing * i + 4, y + (line_offset + 1) * (self.spacing // 2))

    def layout_accidental(self, x: int, y: int, line_offset: int, glyph: str):
        self.add_label(
            glyph, GlyphType.ACCIDENTAL, x - 24, y + 10 + (line_offset + 1) * (self.spacing // 2))  # (+ 3) to align
        # glyph with staff

    def layout_left_barline(self, x, y):
        # only if Barline is on left
        if _DEBUG:
            print('l-barline=', self.measure.barline)
        if isinstance(self.measure.barline, Barline):
            barline_label = self.add_label(
                self.measure.barline.barlinetype.glyph, GlyphType.BARLINE, x=x, y=y + (self.area_height//2))
            x += 18 + barline_label.content_width
        elif isinstance(self.measure.barline, BarlineType):
            barline_verts = list()
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x)
            barline_verts.append(y + self.area_height)
            self.barlines.append(barline_verts)
            x += 18
        return x, y

    def layout_right_barline(self, x, y):
        if isinstance(self.measure.barline, Barline):
            barline_label = Glyph(gtype=self.measure.barline.barlinetype,
                                  glyph=self.measure.barline.barlinetype.glyph,
                                  text=Glyph.code(
                                      self.measure.barline.barlinetype.glyph),
                                  font_name=self._cfg.MUSIC_FONT_NAME,
                                  x=x, y=y + (self.area_height//2),
                                  anchor_x='center',
                                  anchor_y='center')
            barline_label.color = (0, 0, 0, 255)

            barline_verts = list()
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x + barline_label.content_width)
            barline_verts.append(y + self.area_height)
            self.irr_barlines.append(barline_verts)
            self.irr_barline_labels.append(barline_label)
            x += 18 + barline_label.content_width
        elif isinstance(self.measure.barline, BarlineType):
            barline_verts = list()
            barline_verts.append(x)
            barline_verts.append(y)
            barline_verts.append(x)
            barline_verts.append(y + self.area_height)
            self.barlines.append(barline_verts)
        x += -18
        return x, y

    def layout_clef(self, x: int, y: int) -> tuple:
        if self.index == 0:
            x += 12
            clef_pitch = self.measure.clef.value
            # base is treble (G) clef

            match clef_pitch:
                case 53:  # bass clef
                    clef_offset = (self.spacing // 2) * 5 + 10
                case 60:  # alto clef
                    clef_offset = (self.spacing // 2) * 3 + 10
                case _:
                    clef_offset = self.spacing // 2 + 10
            clef_label = self.add_label(
                self.measure.clef.glyph, GlyphType.CLEF, x=x, y=y + self.spacing * 2 + clef_offset)
            x += clef_label.content_width + 10
        return x, y

    def layout_time_signature(self, x: int, y: int) -> tuple:
        if self.index == 0:
            time_sig = self.measure.time
            if time_sig.timesymboltype.__str__() == 'common':
                time_sig = self.add_label(
                    'timeSigCommon', GlyphType.TIME, x, y=y + self.spacing * 4)
                x += time_sig.content_width + 30  # (+30) x offset
            elif time_sig.timesymboltype.__str__() == 'cut':
                time_sig = self.add_label(
                    'timeSigCutCommon', GlyphType.TIME, x, y=y + self.spacing * 4)
                x += time_sig.content_width + 30  # (+30) x offset
            else:
                numerator_glyph = 'timeSig' + str(time_sig.numerator)
                time_sig_numerator = self.add_label(
                    numerator_glyph, GlyphType.TIME, x, y=y + self.spacing * 5)
                denominator_glyph = 'timeSig' + str(time_sig.denominator)
                self.add_label(
                    denominator_glyph, GlyphType.TIME, x, y=y + self.spacing * 3)

                x += time_sig_numerator.content_width + 30  # (+30) x offset
        return x, y

    def key_sig_accidental_offset(self, note: Note, accidental_type: str) -> int:
        offset = 0

        match note:
            case 'C':
                offset += 8
            case 'D':
                offset += 9
            case 'E':
                offset += 10
            case 'F':
                if accidental_type == 'sharp':
                    offset += 11
                else:
                    offset += 3
            case 'G':
                if accidental_type == 'sharp':
                    offset += 12
                else:
                    offset += 4
            case 'A':
                offset += 5
            case 'B':
                offset += 6

        return offset

    @ staticmethod
    def lookup_key_accidentals(key):
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

    @ staticmethod
    def max_key_sig_width(systems: list[PartSystem]) -> int:
        max_accidentals = 0
        for system in systems:
            for part in system.parts:
                for measure in part.measures:
                    key = measure.key
                    accidentals = MeasureArea.lookup_key_accidentals(str(key))
                    if len(accidentals[0]) > max_accidentals:
                        max_accidentals = len(accidentals[0])
                    elif len(accidentals[1]) > max_accidentals:
                        max_accidentals = len(accidentals[1])
        return max_accidentals

    def layout_key_signature(self, x: int, y: int) -> tuple:
        if self.index == 0:
            key = self.measure.key
            accidentals = self.lookup_key_accidentals(key.__str__())
            if _DEBUG:
                print(key_accidentals[key.__str__()])
            if len(accidentals[0]) == 0 and len(accidentals[1]) == 0:
                accidental_label = self.add_label(
                    'accidentalFlat', GlyphType.ACCIDENTAL, x, y)
                # pass
                x += (accidental_label.content_width + 6) * self.key_sig_width
                self.labels.pop()
            else:
                for note in accidentals[0]:
                    line_offset = self.key_sig_accidental_offset(note, 'sharp')
                    # (+ 10) to align glyph with staff
                    accidental_label = self.add_label(
                        'accidentalSharp', GlyphType.ACCIDENTAL, x, y + 10 + line_offset * (self.spacing // 2))
                    x += accidental_label.content_width + 4  # (+4) x offset
                for note in accidentals[1]:
                    line_offset = self.key_sig_accidental_offset(note, 'flat')
                    # (+ 10) to align glyph with staff
                    accidental_label = self.add_label(
                        'accidentalFlat', GlyphType.ACCIDENTAL, x, y + 10 + line_offset * (self.spacing // 2))
                    x += accidental_label.content_width + 4  # (+4) x offset
        x += 20
        return x, y

    def layout_ledger_lines(self, x: int, y: int, line_offset: int, note: Note) -> None:
        ledger_lines = False
        start_num = 0
        end_num = 0
        x_offset = 0
        # below staff
        if line_offset < 2:
            ledger_lines = True
            start_num = line_offset
            end_num = 3
        # above staff
        elif line_offset > 12:
            ledger_lines = True
            start_num = 11
            end_num = line_offset

        # offset ledger line x for up stem glyph
        if note.value <= 0.125 and len(note.beams) == 0 and str(note.stem) == 'StemType.UP':
            x_offset = self.spacing // 2 - 2

        if ledger_lines:
            num = start_num - 1
            while num < end_num:
                # ledger lines only on odd staff lines
                if num % 2 != 0:
                    ledger_line_verts = list()
                    # - 2 is subjective aesthetics
                    ledger_line_verts.append(x - (self.spacing - 2) - x_offset)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    # - 2 is subjective aesthetics
                    ledger_line_verts.append(x + (self.spacing - 2) - x_offset)
                    ledger_line_verts.append(
                        y + (num - 1) * (self.spacing // 2))
                    self.ledger_lines.append(ledger_line_verts)
                num += 1

    def layout_dynamic_markings(self, x, y):
        # TODO: Fine tune X and Y placement and find a way to make hairpins look cleaner (less line aliasing?)
        # Currently places all dynamic marks below the measure with a hardcoded offset
        # Implement a way to offset vertically based on other elements at location

        glyph = ""
        for mark in self.measure.measure_marks:
            if isinstance(mark, DynamicMark):
                # print("mark type start divisions ==", mark.dynamic_type, mark.start_point, mark.divisions,x)

                if mark.dynamic_type == DynamicType.PIANO or mark.dynamic_type == DynamicType.FORTE:
                    glyph = "dynamic" + str(mark.dynamic_type)[12:].title()
                else:
                    glyph = "dynamic" + mark.dynamic_type.abbr.upper()
                gtype = "GlyphType." + str(mark.dynamic_type)[7:]
                dynamic_mark_label = self.add_label(
                    glyph, gtype, x + (float(mark.start_point/100) * 30 * self._cfg.NOTE_WIDTH), y)
            else:
                x_spacing_start = mark.start_point/mark.divisions * self._cfg.NOTE_WIDTH * 20 * .25
                x_spacing_end = mark.end_point/mark.divisions * self._cfg.NOTE_WIDTH * 20 * .25

                # print("mark type start end divisions ==", mark.dynamic_change_type, mark.start_point, mark.end_point, mark.divisions, x)
                # print("x_spacing_start x_spacing_end ==", x_spacing_start, x_spacing_end)

                if mark.dynamic_change_type == DynamicChangeType.CRESCENDO:
                    self.hairpin_start.append((x + x_spacing_start, y))
                    self.hairpin_end.append((x + x_spacing_end, y))
                else:
                    self.hairpin_start.append((x + x_spacing_end, y))
                    self.hairpin_end.append((x + x_spacing_start, y))
                pass

    def draw(self):
        for label in self.labels:
            label.draw()

    def add_label(self, glyph, gtype, x=0, y=0):
        glyph_id = Glyph.code(glyph)
        note_off = 0

        # if gtype == GlyphType.NOTE_UP:  # Possibly move this elsewear (parameter)
        #     note_off = 20

        label = Glyph(gtype=gtype,
                      glyph=glyph,
                      text=glyph_id,
                      font_name=self._cfg.MUSIC_FONT_NAME,
                      x=x + note_off, y=y,
                      anchor_x='center',
                      anchor_y='center',
                      color=(0, 0, 0, 255),
                      batch=self.batch)
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

    def get_beam_lines(self):
        return self.beam_lines

    def get_stems(self):
        return self.stems
