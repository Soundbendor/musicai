import pyglet
from pyglet import shapes
from pyglet.graphics import Batch
from pyglet.image import SolidColorImagePattern
from visualization.view_area import MeasureArea
from visualization.window_config import WindowConfig

_DEBUG = True
_NUM_BARLINES = 5
_BLACK = (0, 0, 0)
_BACKGROUND = (255, 255, 255, 255)

class ScoreWindow(pyglet.window.Window): # noqa
    def __init__(self, score) -> None:
        self._cfg = WindowConfig()
        super().__init__(
            height=self._cfg.SCREEN_HEIGHT,
            width=self._cfg.SCREEN_WIDTH
        )

        pyglet.font.add_file(self._cfg.MUSIC_FONT_FILE)

        self.batch = Batch()
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
        self.measure_height = self._cfg.MEASURE_HEIGHT
        self.measure_area_width = list()
        self.zoom = 1
        self._initialize_display_elements()
        self.x_movement = 0
        self.y_movement = 0

    def on_draw(self, dt=None) -> None:
        self.clear()
        self.background.blit(0, 0)

        self._update_coordinates()

        self.batch.draw()
        # TODO I'm not sure what this line does or if it needs to be included.
        # pyglet.gl.glFlush()

    def on_key_press(self, symbol, modifiers) -> None:
        match symbol:
            case self._cfg.KEYBIND_UP:
                self.y_movement = -1 * self._cfg.FAST_MOVEMENT
            case self._cfg.KEYBIND_DOWN:
                self.y_movement = self._cfg.FAST_MOVEMENT
            case self._cfg.KEYBIND_LEFT:
                self.x_movement = self._cfg.FAST_MOVEMENT
            case self._cfg.KEYBIND_RIGHT:
                self.x_movement = -1 * self._cfg.FAST_MOVEMENT
            case self._cfg.KEYBIND_EXIT:
                self.close()
            case _:
                pass

    def on_key_release(self, symbol, modifiers) -> None:
        match symbol:
            case self._cfg.KEYBIND_UP | self._cfg.KEYBIND_DOWN:
                self.y_movement = 0
            case self._cfg.KEYBIND_LEFT | self._cfg.KEYBIND_RIGHT:
                self.x_movement = 0
            case _:
                pass

    def on_mouse_leave(self, x, y) -> None:
        self.x_movement = 0
        self.y_movement = 0

    # TODO: Do we want each measure length to be a separate segment?
    def max_key_sig_width(self) -> int:
        max_accidentals = 0
        for system in self.score.systems:
            for part in system.parts:
                for measure in part.measures:
                    accidentals = MeasureArea.lookup_key_accidentals(str(measure.key))
                    max_accidentals = len(accidentals[0]) if len(accidentals[0]) > max_accidentals \
                        else len(accidentals[1])
        return max_accidentals

    def _draw_measure(self, x_start: int, measure_length: int, y: int) -> None:
        for index in range(_NUM_BARLINES):
            y_value = y + index * (self._cfg.MEASURE_LINE_SPACING * self.zoom)
            x_end = (x_start + measure_length) * self.zoom

            bar_line = shapes.Line(
                x_start, y_value, x_end, y_value, width=2, color=_BLACK, batch=self.batch)

            self.measures.append(bar_line)

    def _draw_measures(self) -> None:
        for num_parts in range(len(self.score.systems[0].parts)):
            total_width = 0
            measure_length = self.height - self._cfg.TOP_OFFSET - (num_parts * self._cfg.MEASURE_OFFSET)

            for num_measures in range(len(self.score.systems[0].parts[0].measures)):
                measure_width = self.measure_area_width[num_measures]
                self._draw_measure(total_width, measure_width, measure_length)

                total_width += measure_width

    def _draw_hairpins(self) -> None:
        for index in range(len(self.hairpin_start_verts)):
            y = self.hairpin_start_verts[index][1]
            x_start = self.hairpin_start_verts[index][0]
            x_end = self.hairpin_end_verts[index][0]
            # TODO magic number: 15, what does this signify?
            hairpin_line_top = shapes.Line(x_start, y, x_end, y + 15, width=2, color=_BLACK, batch=self.batch)
            hairpin_line_bottom = shapes.Line(x_start, y, x_end, y - 15, width=2, color=_BLACK, batch=self.batch)
            self.hairpin_lines.append(hairpin_line_top)
            self.hairpin_lines.append(hairpin_line_bottom)

    def _draw_ledger_lines(self) -> None:
        for line in self.ledger_line_verts:
            ledger_line = shapes.Line(
                line[0], line[1], line[2], line[3], width=2, color=_BLACK, batch=self.batch)
            self.ledger_lines.append(ledger_line)

    #TODO: This function is not called, do we still need it?
    def load_barlines(self, measure_area) -> None:
        self.barlines.append(measure_area.get_barlines())

    def load_labels(self, x, y) -> None:
        key_sig_width = self.max_key_sig_width()
        for system in self.score.systems:
            for i in range(len(system.parts[0].measures)):
                max_measure_area = 0
                # TODO: Same loop in two places - for part in system.parts
                for part in system.parts:
                    measure_area = MeasureArea(
                        part.measures[i], x, y, self.measure_height, key_sig_width, i, batch=self.batch)
                    if measure_area.area_width > max_measure_area:
                        max_measure_area = measure_area.area_width
                self.measure_area_width.append(int(max_measure_area))

            # TODO: Same loop in two places - for part in system.parts
            for part in system.parts:
                for measure_idx, measure in enumerate(part.measures):
                    measure_area = MeasureArea(
                        measure, x, y, self.measure_height, key_sig_width,
                        measure_idx, self.measure_area_width[measure_idx], batch=self.batch)
                    # TODO calc and set area_width
                    # x += measure_area.area_width
                    x += self.measure_area_width[measure_idx]
                    self.labels.extend(measure_area.labels)
                    self.barlines.extend(measure_area.barlines)
                    self.ledger_line_verts.extend(measure_area.ledger_lines)
                    self.hairpin_start_verts.extend(measure_area.hairpin_start)
                    self.hairpin_end_verts.extend(measure_area.hairpin_end)

                    if measure.has_irregular_rs_barline():
                        self.irr_barlines.extend(measure_area.irr_barlines)
                        barline_idx = measure_area.irr_barlines_idx

                        for idx in barline_idx:
                            if idx not in self.irr_barlines_idx:
                                self.irr_barlines_idx.append(idx)
                x = 0
                y -= self._cfg.MEASURE_OFFSET

    def _initialize_display_elements(self) -> None:
        self.background = SolidColorImagePattern(color=_BACKGROUND).create_image(self.width, self.height)
        self.load_labels(0, self.height - self._cfg.TOP_OFFSET)
        self._draw_measures()
        self._draw_ledger_lines()
        self._draw_hairpins()

        for i in range(len(self.irr_barlines_idx)):
            x_start = self.irr_barlines[i][0]
            y_start = self.irr_barlines[i][1]
            x_end = self.irr_barlines[i][2]
            y_end = self.irr_barlines[i][3]
            for vert in self.irr_barlines:
                if vert[0] == x_start:
                    y_start = vert[1]
            if self._is_repeatright_glyph(i):
                x_start = x_start + 4
                x_end = x_end - 10
                rectangle = shapes.Rectangle(
                    x_start, y_start,  x_end - x_start, y_end - y_start, color=_BLACK, batch=self.batch)
                line = shapes.Line(x_start - 5, y_start, x_start-5,
                                   y_end, width=1, color=_BLACK, batch=self.batch)
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
            line = shapes.Line(x, y_start, x, y_end, width=2, color=_BLACK, batch=self.batch)
            self.barline_shapes.append(line)

    def _is_repeatright_glyph(self, index):
        return self.score.systems[0].parts[0].measures[self.irr_barlines_idx[index]].\
                   barline.barlinetype.glyph == 'repeatRight'

    def display(self) -> None:
        pyglet.app.run()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        self._x_mouse_movement(x)
        self._y_mouse_movement(y)

    def _x_mouse_movement(self, x_coord) -> None:
        self.x_movement = self._mouse_movement_speed(x_coord, self._cfg.SCREEN_WIDTH)

    def _y_mouse_movement(self, y_coord) -> None:
        self.y_movement = self._mouse_movement_speed(y_coord, self._cfg.SCREEN_HEIGHT)

    def _mouse_movement_speed(self, coord, size) -> int:
        if coord < (size // self._cfg.FAST_SIZE):
            speed = self._cfg.FAST_MOVEMENT
        elif coord < (size // self._cfg.SLOW_SIZE):
            speed = self._cfg.SLOW_MOVEMENT
        elif coord > (size - self._cfg.SCREEN_WIDTH // self._cfg.FAST_SIZE):
            speed = -1 * self._cfg.FAST_MOVEMENT
        elif coord > (size - self._cfg.SCREEN_WIDTH // self._cfg.SLOW_SIZE):
            speed = -1 * self._cfg.SLOW_MOVEMENT
        else:
            speed = 0

        return speed

    def _update_coordinates(self) -> None:
        self._update_x()
        self._update_y()

    def _update_x(self) -> None:
        self._update_axis("x", self.x_movement)

    def _update_y(self) -> None:
        self._update_axis("y", self.y_movement)

    def _update_axis(self, axis: str, movement: int) -> None:
        collections = [self.labels, self.measures,
                       self.barline_shapes, self.ledger_lines,
                       self.hairpin_lines]

        for collection in collections:
            for item in collection:
                ScoreWindow._set_movement(item, axis, movement)

    @staticmethod
    def _set_movement(item: any, axis: str, movement: int) -> None:
        new_movement = getattr(item, axis) + movement
        setattr(item, axis, new_movement)
