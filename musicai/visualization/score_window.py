import pyglet
from pyglet import shapes

from fileio.mxml import Score
from visualization.view_area import MeasureArea, Staff, LedgerLine
from visualization.window_config import WindowConfig
from structure.score import PartSystem

_DEBUG = True
_RGB_BLACK = (0, 0, 0)

class ScoreWindow(pyglet.window.Window): # noqa
    def __init__(self, score: Score, window_config: WindowConfig) -> None:
        self._cfg = window_config

        config = pyglet.gl.Config(sample_buffers=1,buffers=4,double_buffer=True)
        super(ScoreWindow, self).__init__(
            height=self._cfg.SCREEN_HEIGHT,
            width=self._cfg.SCREEN_WIDTH,
            #config=config
        )

        pyglet.font.add_file(self._cfg.MUSIC_FONT_FILE)
        bravura = pyglet.font.load(self._cfg.MUSIC_FONT_NAME)

        self.batch = pyglet.graphics.Batch()
        self.staff_lines = list()
        self.barlines = list()
        self.irr_barlines = list()
        self.irr_barline_labels = list()
        self.barline_shapes = list()
        self.ledger_line_verts = list()
        self.ledger_lines = list()
        self.beam_line_verts = list()
        self.beam_lines = list()
        self.stem_verts = list()
        self.stems = list()
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

    def draw_hairpins(self) -> None:
        for i in range(len(self.hairpin_start_verts)):
            y = self.hairpin_start_verts[i][1]
            x_start = self.hairpin_start_verts[i][0]
            x_end = self.hairpin_end_verts[i][0]
            hairpin_line_top = shapes.Line(x_start, y, x_end, y + 15, width=2, color=_RGB_BLACK, batch=self.batch)
            hairpin_line_bottom = shapes.Line(x_start, y, x_end, y - 15, width=2, color=_RGB_BLACK, batch=self.batch)
            self.hairpin_lines.append(hairpin_line_top)
            self.hairpin_lines.append(hairpin_line_bottom)

    def _draw_beams(self):
        for line in self.beam_line_verts:
            beam_line = shapes.Line(
                line[0], line[1], line[2], line[3], width=8, color=(0, 0, 0), batch=self.batch)
            # beam_line = shapes.Polygon(
            #     [line[0], line[1], line[2], line[3], line[0], line[1] + 5, line[2], line[3] + 5, line[0], line[1]], color=(0, 0, 0), batch=self.batch)
            self.beam_lines.append(beam_line)

    def _draw_stems(self):
        for line in self.stem_verts:
            stem = shapes.Line(
                line[0], line[1], line[2], line[3], width=2, color=(0, 0, 0), batch=self.batch)
            self.stems.append(stem)

    def load_barlines(self, measure_area):
        self.barlines.append(measure_area.get_barlines())

    def load_labels(self, x: int = 0, y: int = 0, systems: list[PartSystem] = None) -> None:
        key_sig_width = MeasureArea.max_key_sig_width(systems)
        for system in self.score.systems:
            for measure_idx in range(len(system.parts[0].measures)):
                max_measure_area = 0
                measure_area_barlines = list()
                measure_area_irr_barlines = list()
                measure_area_irr_barline_labels = list()
                start_y  =  y 

                for part in system.parts:
                    measure_area = MeasureArea(
                        part.measures[measure_idx], x, y, self.measure_height, key_sig_width, measure_idx,  x, config=self._cfg, batch=self.batch)
                    if measure_area.area_width > max_measure_area:
                        max_measure_area = measure_area.area_width

                    self.labels.extend(measure_area.labels)
                    self.ledger_line_verts.extend(measure_area.ledger_lines)
                    self.hairpin_start_verts.extend(measure_area.hairpin_start)
                    self.hairpin_end_verts.extend(measure_area.hairpin_end)
                    self.beam_line_verts.extend(measure_area.beam_lines)
                    self.stem_verts.extend(measure_area.stems)

                    measure_area_barlines.extend(measure_area.barlines)
                    measure_area_irr_barlines.extend(measure_area.irr_barlines)
                    measure_area_irr_barline_labels.extend(measure_area.irr_barline_labels)

                    y -= self._cfg.MEASURE_OFFSET
                
                for barline_verts in measure_area_barlines:
                    if barline_verts[0] != 0:
                        barline_verts[0] = int(x + max_measure_area)
                        barline_verts[2] = int(x +max_measure_area)
                
                if measure_area.measure.has_irregular_rs_barline():
                    for irr_barline_label in measure_area_irr_barline_labels:
                        irr_barline_label.x = int(x+ max_measure_area)
                        irr_barline_label.batch = self.batch
                    for irr_barline_verts in measure_area_irr_barlines:
                        if irr_barline_verts[0] != 0:
                            irr_barline_verts[0] = int(x + max_measure_area)
                            irr_barline_verts[2] = int(x + max_measure_area + measure_area.irr_barline_labels[0].content_width)
                    
                self.barlines.extend(measure_area_barlines)
                self.irr_barlines.extend(measure_area_irr_barlines)
                self.irr_barline_labels.extend(measure_area_irr_barline_labels)
                
                self.measure_area_width.append(max_measure_area)
                x += max_measure_area
                y = start_y
            
            for part in system.parts:
                y -= self._cfg.MEASURE_OFFSET
            x = 0
            


    def _initialize_display_elements(self) -> None:
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)
        self.load_labels(0, self.height - self._cfg.TOP_OFFSET, self.score.systems)

        num_parts = len(self.score.systems[0].parts)
        self.staff_lines = Staff(num_parts=num_parts, measure_widths=self.measure_area_width,
                                 height=self.height, batch=self.batch).staff_lines()
        self.ledger_lines = LedgerLine(ledger_coords=self.ledger_line_verts, batch=self.batch).ledger_lines()
        self._draw_beams()
        self._draw_stems()
        self.draw_hairpins()
        self.draw_barlines()
        self.draw_irr_barlines()

    def draw_irr_barlines(self):
        for i in range(len(self.irr_barline_labels)):
            x_start = self.irr_barlines[i][0]
            y_start = self.irr_barlines[i][1]
            x_end = self.irr_barlines[i][2]
            y_end = self.irr_barlines[i][3]

            for vert in self.irr_barlines:
                if vert[0] == x_start:
                    y_start = vert[1]
            if (self.irr_barline_labels[0].gtype.glyph == 'repeatRight'):
                x_start = x_start + 4
                x_end = x_end - 10
                rectangle = shapes.Rectangle(
                    x_start, y_start,  x_end - x_start, y_end - y_start, color=_RGB_BLACK, batch=self.batch)
                line = shapes.Line(x_start - 5, y_start, x_start-5,
                                   y_end, width=1, color=_RGB_BLACK, batch=self.batch)
                self.barline_shapes.append(rectangle)
                self.barline_shapes.append(line)
        # TODO Modify the connecting barline shapes for different irregular barlines
        

    def draw_barlines(self) -> None:
        for i in range(len(self.barlines)):
            x = self.barlines[i][0]
            y_start = self.barlines[i][1]
            y_end = self.barlines[i][3]
            for vert in self.barlines[i:]:
                if vert[0] == x:
                    y_start = vert[1]
            line = shapes.Line(x, y_start, x, y_end, width=2, color=_RGB_BLACK, batch=self.batch)
            self.barline_shapes.append(line)

    def on_draw(self, dt=None) -> None:
        self.clear()
        self.background.blit(0, 0)

        self._update_coordinates()

        self.batch.draw()
        # TODO I'm not sure what this line does or if it needs to be included.
        # pyglet.gl.glFlush()

    def display(self) -> None:
        pyglet.app.run()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self._x_mouse_movement(x)
        self._y_mouse_movement(y)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        if _DEBUG:
            print(f"scroll - x: {x}, y: {y}, scroll_x: {scroll_x}, scroll_y: {scroll_y}")

    def _x_mouse_movement(self, x_coord: int) -> None:
        self.x_movement = self._mouse_movement_speed(x_coord, self._cfg.SCREEN_WIDTH)

    def _y_mouse_movement(self, y_coord: int) -> None:
        self.y_movement = self._mouse_movement_speed(y_coord, self._cfg.SCREEN_HEIGHT)

    def _mouse_movement_speed(self, coord: int, size: int) -> int:
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

    def on_mouse_leave(self, x: int, y: int) -> None:
        self.x_movement = 0
        self.y_movement = 0

    def _update_coordinates(self) -> None:
        self._update_x()
        self._update_y()

    def _update_x(self) -> None:
        self._update_axis("x", self.x_movement)

    def _update_y(self) -> None:
        self._update_axis("y", self.y_movement)

    def _update_axis(self, axis: str, movement: int) -> None:
        collections = [self.labels, self.staff_lines,
                       self.barline_shapes, self.ledger_lines,
                       self.hairpin_lines, self.beam_lines, self.stems]

        for collection in collections:
            for item in collection:
                ScoreWindow._set_movement(item, axis, movement)

    @staticmethod
    def _set_movement(item: any, axis: str, movement: int) -> None:
        new_movement = getattr(item, axis) + movement
        setattr(item, axis, new_movement)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
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

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case self._cfg.KEYBIND_UP | self._cfg.KEYBIND_DOWN:
                self.y_movement = 0
            case self._cfg.KEYBIND_LEFT | self._cfg.KEYBIND_RIGHT:
                self.x_movement = 0
            case _:
                pass
