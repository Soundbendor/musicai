import pyglet
from pyglet import shapes, gl
from pyglet.window import key

import json

from fileio.mxml import MusicXML
from visualization.view_area import MeasureArea
from visualization.window_config import WindowConfig
from visualization.view_area import key_accidentals

_DEBUG = True


class ScoreWindow(pyglet.window.Window):
    def __init__(self, score):
        self.msvcfg = WindowConfig()
        super(ScoreWindow, self).__init__(
            height=self.msvcfg.SCREEN_HEIGHT, width=self.msvcfg.SCREEN_WIDTH)

        pyglet.font.add_file(self.msvcfg.MUSIC_FONT_FILE)
        bravura = pyglet.font.load(self.msvcfg.MUSIC_FONT_NAME)

        # TODO: What does label do and do we need it?
        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name=self.msvcfg.MUSIC_FONT_NAME,
                                       font_size=int(
                                           self.msvcfg.MUSIC_FONT_SIZE),
                                       x=self.width // 2, y=self.height // 2,
                                       anchor_x='center', anchor_y='center')
        self.label.color = (0, 0, 0, 255)

        self.batch = pyglet.graphics.Batch()
        self.measures = list()
        self.barlines = list()
        self.irr_barlines = list()
        self.irr_barlines_idx = list()
        self.barline_shapes = list()
        self.ledger_line_verts = list()
        self.ledger_lines = list()
        self.hairpin_start_verts = list()
        self.hairpin_end_verts = list()
        self.hairpin_lines = list()

        self.score = score

        self.labels = list()
        self.measure_height = int(self.msvcfg.MEASURE_HEIGHT)
        self.measure_area_width = list()
        self.zoom = 1
        self._initialize_display_elements()
        self.x_movement = 0
        self.y_movement = 0

    # TODO: Do we want each measure length to be a separate segment?

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

    def max_key_sig_width(self):
        max_accidentals = 0
        for system in self.score.systems:
            for part in system.parts:
                for measure in part.measures:
                    key = measure.key
                    accidentals = self.lookup_key_accidentals(key.__str__())
                    if len(accidentals[0]) > max_accidentals:
                        max_accidentals = len(accidentals[0])
                    elif len(accidentals[1]) > max_accidentals:
                        max_accidentals = len(accidentals[1])
        return max_accidentals

    def _draw_measure(self, x_start, measure_length, y):
        for i in range(5):
            y_value = y + i * (self.msvcfg.MEASURE_LINE_SPACING * self.zoom)
            x_end = (x_start + measure_length) * self.zoom

            bar_line = shapes.Line(
                x_start, y_value, x_end, y_value, width=2, color=(0, 0, 0), batch=self.batch)

            self.measures.append(bar_line)

    def _draw_measures(self):
        for num_parts in range(len(self.score.systems[0].parts)):
            total_width = 0

            for num_measures in range(len(self.score.systems[0].parts[0].measures)):
                measure_width = self.measure_area_width[num_measures]
                measure_length = self.height - self.msvcfg.TOP_OFFSET - \
                    (num_parts * self.msvcfg.MEASURE_OFFSET)

                self._draw_measure(total_width, measure_width, measure_length)

                total_width += measure_width
    """
    def _draw_measure(self, x, y):
        for i in range(5):
            y_value = y + i * (self.msvcfg.MEASURE_LINE_SPACING * self.zoom)
            x_start = 0
            x_end = x * self.zoom
            bar_line = shapes.Line(x_start, y_value, x_end, y_value, width=2, color=(0, 0, 0), batch=self.batch)
            self.measures.append(bar_line)

    def _draw_measures(self):
        total_width = sum(self.measure_area_width)
        for num_parts in range(len(self.score.systems[0].parts)):
            part_height = self.height - self.msvcfg.TOP_OFFSET - (num_parts * self.msvcfg.MEASURE_OFFSET)
            self._draw_measure(total_width, part_height)
    """
    def draw_hairpins(self):
        for i in range(len(self.hairpin_start_verts)):
            y = self.hairpin_start_verts[i][1]
            x_start = self.hairpin_start_verts[i][0]
            x_end = self.hairpin_end_verts[i][0]
            hairpin_line_top = shapes.Line(x_start, y, x_end, y + 15, width=2, color=(0,0,0), batch=self.batch)
            hairpin_line_bottom = shapes.Line(x_start, y, x_end, y - 15, width=2, color=(0,0,0), batch=self.batch)
            self.hairpin_lines.append(hairpin_line_top)
            self.hairpin_lines.append(hairpin_line_bottom)

    def _draw_ledger_lines(self):
        for line in self.ledger_line_verts:
            ledger_line = shapes.Line(
                line[0], line[1], line[2], line[3], width=2, color=(0, 0, 0), batch=self.batch)
            self.ledger_lines.append(ledger_line)

    def load_barlines(self, measure_area):
        self.barlines.append(measure_area.get_barlines())

    def load_labels(self, x, y):
        key_sig_width = self.max_key_sig_width()
        for system in self.score.systems:
            for i in range(len(system.parts[0].measures)):
                max_measure_area = 0
                for part in system.parts:
                    measure_area = MeasureArea(
                        part.measures[i], x, y, self.measure_height, key_sig_width, i)
                    if (measure_area.area_width > max_measure_area):
                        max_measure_area = measure_area.area_width
                self.measure_area_width.append(int(max_measure_area))

            for part in system.parts:
                for idx, measure in enumerate(part.measures):
                    measure_area = MeasureArea(
                        measure, x, y, self.measure_height, key_sig_width, idx, self.measure_area_width[idx])
                    # TODO calc and set area_width
                    # x += measure_area.area_width
                    x += self.measure_area_width[idx]
                    measure_labels = measure_area.get_labels()
                    for label in measure_labels:
                        label.batch = self.batch
                        self.labels.append(label)
                    barline_verts = measure_area.get_barlines()
                    for vert in barline_verts:
                        self.barlines.append(vert)
                    ledger_line_verts = measure_area.get_ledger_lines()
                    for vert in ledger_line_verts:
                        if (len(vert) != 0):
                            self.ledger_line_verts.append(vert)
                    hairpin_start_verts = measure_area.get_hairpin_start()
                    for vert in hairpin_start_verts:
                        self.hairpin_start_verts.append(vert)
                    hairpin_end_verts = measure_area.get_hairpin_end()
                    for vert in hairpin_end_verts:
                        self.hairpin_end_verts.append(vert)
                    if (measure.has_irregular_rs_barline()):
                        barline_irr_verts = measure_area.get_irr_barlines()
                        barline_idx = measure_area.get_irr_barlines_idx()
                        for vert in barline_irr_verts:
                            self.irr_barlines.append(vert)
                        for idx in barline_idx:
                            if idx not in self.irr_barlines_idx:
                                self.irr_barlines_idx.append(idx)
                x = 0
                y -= self.msvcfg.MEASURE_OFFSET

    def _initialize_display_elements(self):
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)
        self.load_labels(0, self.height - int(self.msvcfg.TOP_OFFSET))
        self._draw_measures()
        self._draw_ledger_lines()
        self.draw_hairpins()

        for i in range(len(self.irr_barlines_idx)):
            x_start = self.irr_barlines[i][0]
            y_start = self.irr_barlines[i][1]
            x_end = self.irr_barlines[i][2]
            y_end = self.irr_barlines[i][3]
            for vert in self.irr_barlines:
                if vert[0] == x_start:
                    y_start = vert[1]
            if (self.score.systems[0].parts[0].measures[self.irr_barlines_idx[i]].barline.barlinetype.glyph == 'repeatRight'):
                x_start = x_start + 4
                x_end = x_end - 10
                rectangle = shapes.Rectangle(
                    x_start, y_start,  x_end - x_start, y_end - y_start, color=(0, 0, 0), batch=self.batch)
                line = shapes.Line(x_start - 5, y_start, x_start-5,
                                   y_end, width=1, color=(0, 0, 0), batch=self.batch)
                self.barline_shapes.append(rectangle)
                self.barline_shapes.append(line)
            # TODO Modify the connecting barline shapes for different irregular barlines

        for i in range(len(self.barlines)):
            x = self.barlines[i][0]
            y_start = self.barlines[i][1]
            y_end = self.barlines[i][3]
            for vert in self.barlines[i:]:
                if vert[0] == x:
                    y_start = vert[1]
            line = shapes.Line(x, y_start, x, y_end, width=2, color=(0,0,0), batch=self.batch)
            self.barline_shapes.append(line)

        # for i in range(len(self.score.systems[0].parts[0].measures)):
        #     x = self.barlines[i][0]
        #     y_start = self.barlines[i][1]
        #     y_end = self.barlines[i][3]

        #     for vert in self.barlines:
        #         if vert[0] == x:
        #             y_start = vert[1]
        #     line = shapes.Line(x, y_start, x, y_end, width=2,
        #                        color=(0, 0, 0), batch=self.batch)
        #     self.barline_shapes.append(line)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)

        self._update_coordinates()

        self.batch.draw()
        # TODO I'm not sure what this line does or if it needs to be included.
        # pyglet.gl.glFlush()

    def display(self):
        pyglet.app.run()

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_leave(self, x, y):
        pass

    def _update_coordinates(self):
        self._update_x()
        self._update_y()

    def _update_x(self):
        for label in self.labels:
            label.x += self.x_movement
        for measure in self.measures:
            measure.x += self.x_movement
        for barline_shape in self.barline_shapes:
            barline_shape.x += self.x_movement
        for ledger_line in self.ledger_lines:
            ledger_line.x += self.x_movement
        for hairpin_line in self.hairpin_lines:
            hairpin_line.x += self.x_movement

    def _update_y(self):
        for label in self.labels:
            label.y += self.y_movement
        for measure in self.measures:
            measure.y += self.y_movement
        for barline_shape in self.barline_shapes:
            barline_shape.y += self.y_movement
        for ledger_line in self.ledger_lines:
            ledger_line.y += self.y_movement
        for hairpin_line in self.hairpin_lines:
            hairpin_line.y += self.y_movement

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case self.msvcfg.KEYBIND_UP:
                self.y_movement = -1 * int(self.msvcfg.FAST_MOVEMENT)
            case self.msvcfg.KEYBIND_DOWN:
                self.y_movement = int(self.msvcfg.FAST_MOVEMENT)
            case self.msvcfg.KEYBIND_LEFT:
                self.x_movement = int(self.msvcfg.FAST_MOVEMENT)
            case self.msvcfg.KEYBIND_RIGHT:
                self.x_movement = -1 * int(self.msvcfg.FAST_MOVEMENT)
            case self.msvcfg.KEYBIND_EXIT:
                self.close()
            case _:
                pass

    def on_key_release(self, symbol, modifiers):
        match symbol:
            case self.msvcfg.KEYBIND_UP:
                self.y_movement = 0
            case self.msvcfg.KEYBIND_DOWN:
                self.y_movement = 0
            case self.msvcfg.KEYBIND_LEFT:
                self.x_movement = 0
            case self.msvcfg.KEYBIND_RIGHT:
                self.x_movement = 0
            case _:
                pass
