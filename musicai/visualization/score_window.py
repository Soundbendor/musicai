import pyglet
from pyglet import shapes
from pyglet.gl import *

from fileio.mxml import Score
from visualization.view_area import MeasureArea, Staff, LedgerLine
from visualization.window_config import WindowConfig
from structure.score import PartSystem
from structure.measure import BarlineType

_DEBUG = True
_RGB_BLACK = (0, 0, 0)


class ScoreWindow(pyglet.window.Window):  # noqa
    def __init__(self, score: Score, window_config: WindowConfig) -> None:
        self._cfg = window_config

        config = pyglet.gl.Config(sample_buffers=1, buffers=4, double_buffer=True)
        super(ScoreWindow, self).__init__(
            height=self._cfg.SCREEN_HEIGHT,
            width=self._cfg.SCREEN_WIDTH,
            caption="Score Visualization",
            resizable=True
            # config=config
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
        self.slur_start_verts = list()
        self.slur_end_verts = list()
        self.tie_start_verts = list()
        self.tie_end_verts = list()
        self.slur_arcs = list()
        self.tie_arcs = list()

        self.score = score

        self.labels = list()
        self.measure_height = self._cfg.MEASURE_HEIGHT
        self.measure_area_width = list()
        self.zoom = 1
        self.score_width = 0
        self.score_height = 0
        self.background = None
        self._initialize_display_elements()
        self.x_movement = 0
        self.y_movement = 0
        self.camera_x = 0
        self.camera_y = 0
        x, y = self.get_location()
        # maximum/minimum sizes of window
        #   (note: this is background size, when increasing maximum size also increase background size)
        self.set_maximum_size(1440, 1080)
        self.set_minimum_size(640, 480)

        # below are for info sprite and info layout
        self.info_img = pyglet.image.load('./visualization/assets/info_img.png')
        self.info_sprite = pyglet.sprite.Sprite(self.info_img, x=5, y=10)
        self.info_sprite.scale = 0.5
        self.display_info = False
        self.info_layout = None
        self.info_batch = pyglet.graphics.Batch()
        self.generate_info_layout()
        self.sprite_x1 = self.info_sprite.x
        self.sprite_x2 = self.info_sprite.x + self.info_sprite.width
        self.sprite_y1 = self.info_sprite.y
        self.sprite_y2 = self.info_sprite.y + self.info_sprite.height

    '''
    Sets new values window dimensions in config file after resize
    '''
    def on_resize(self, width: float, height: float):
        self._cfg.SCREEN_WIDTH = self.width
        self._cfg.SCREEN_HEIGHT = self.height
        if self.info_layout:
            self.info_layout.y = self.height - 150

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
            self.beam_lines.append(beam_line)

    def _draw_stems(self):
        for line in self.stem_verts:
            stem = shapes.Line(
                line[0], line[1], line[2], line[3], width=2, color=(0, 0, 0), batch=self.batch)
            self.stems.append(stem)

    def _draw_arc(self, x_start, y_start, x_end, y_end):
        arc_labels = list()
        arc_height = 50
        arc_horizontal_offset = 20

        main_arc = shapes.BezierCurve((x_start, y_start),
                                      (x_start + arc_horizontal_offset, y_start + arc_height),
                                      (x_end - arc_horizontal_offset, y_end + arc_height),
                                      (x_end, y_end),
                                      t=1,
                                      segments=100,
                                      color=_RGB_BLACK,
                                      batch=self.batch)
        main_arc.position = (x_start, y_start)
        arc_labels.append(main_arc)
        for i in range(1, WindowConfig().MUSIC_ARC_SIZE):
            upper_arc = shapes.BezierCurve((x_start, y_start),
                                           (x_start + arc_horizontal_offset, y_start + arc_height + i),
                                           (x_end - arc_horizontal_offset, y_end + arc_height + i),
                                           (x_end, y_end),
                                           t=1,
                                           segments=100,
                                           color=_RGB_BLACK,
                                           batch=self.batch)
            lower_arc = shapes.BezierCurve((x_start, y_start),
                                           (x_start + arc_horizontal_offset, y_start + arc_height - i),
                                           (x_end - arc_horizontal_offset, y_end + arc_height - i),
                                           (x_end, y_end),
                                           t=1,
                                           segments=100,
                                           color=_RGB_BLACK,
                                           batch=self.batch)

            upper_arc.position = (x_start, y_start)
            lower_arc.position = (x_start, y_start)
            arc_labels.append(upper_arc)
            arc_labels.append(lower_arc)

        return arc_labels

    def _draw_ties(self):
        start_verts_ordered = list()
        end_verts_ordered = list()

        for i in range(len(self.score.systems[0].parts)):
            part_start_ties = list()
            part_end_ties = list()
            for j in range(len(self.tie_start_verts)):
                part_start_ties.extend(self.tie_start_verts[j][i])
            for j in range(len(self.tie_end_verts)):
                part_end_ties.extend(self.tie_end_verts[j][i])
            start_verts_ordered.append(part_start_ties)
            end_verts_ordered.append(part_end_ties)

        self.tie_start_verts = start_verts_ordered
        self.tie_end_verts = end_verts_ordered

        for i in range(len(self.tie_end_verts)):
            for j in range(len(self.tie_end_verts[i])):
                x_start = self.tie_start_verts[i][j][0]
                x_end = self.tie_end_verts[i][j][0]
                y_start = self.tie_start_verts[i][j][1]
                y_end = self.tie_end_verts[i][j][1]

                drawn_arcs = self._draw_arc(x_start, y_start, x_end, y_end)
                self.tie_arcs.extend(drawn_arcs)

    def _draw_slurs(self):
        start_verts_ordered = list()
        end_verts_ordered = list()

        for i in range(len(self.score.systems[0].parts)):
            part_start_slurs = list()
            part_end_slurs = list()
            for j in range(len(self.slur_start_verts)):
                part_start_slurs.extend(self.slur_start_verts[j][i])
            for j in range(len(self.slur_end_verts)):
                part_end_slurs.extend(self.slur_end_verts[j][i])
            start_verts_ordered.append(part_start_slurs)
            end_verts_ordered.append(part_end_slurs)

        self.slur_start_verts = start_verts_ordered
        self.slur_end_verts = end_verts_ordered

        for i in range(len(self.slur_end_verts)):
            for j in range(len(self.slur_end_verts[i])):
                x_start = self.slur_start_verts[i][j][0]
                x_end = self.slur_end_verts[i][j][0]
                y_start = self.slur_start_verts[i][j][1]
                y_end = self.slur_end_verts[i][j][1]

                drawn_arcs = self._draw_arc(x_start, y_start, x_end, y_end)
                self.slur_arcs.extend(drawn_arcs)

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
                measure_area_start_slurs = list()
                measure_area_end_slurs = list()
                measure_area_start_ties = list()
                measure_area_end_ties = list()
                start_y = y

                for part in system.parts:
                    measure_area = MeasureArea(
                        part.measures[measure_idx], x, y, self.measure_height, key_sig_width, measure_idx, x,
                        config=self._cfg, batch=self.batch)
                    if measure_area.area_width > max_measure_area:
                        max_measure_area = measure_area.area_width

                    self.labels.extend(measure_area.labels)
                    self.ledger_line_verts.extend(measure_area.ledger_lines)
                    self.hairpin_start_verts.extend(measure_area.hairpin_start)
                    self.hairpin_end_verts.extend(measure_area.hairpin_end)
                    self.beam_line_verts.extend(measure_area.beam_lines)
                    self.stem_verts.extend(measure_area.stems)

                    measure_area_start_slurs.append(measure_area.slur_start)
                    measure_area_end_slurs.append(measure_area.slur_end)
                    measure_area_start_ties.append(measure_area.tie_start)
                    measure_area_end_ties.append(measure_area.tie_end)
                    measure_area_barlines.extend(measure_area.barlines)
                    measure_area_irr_barlines.extend(measure_area.irr_barlines)
                    measure_area_irr_barline_labels.extend(measure_area.irr_barline_labels)

                    y -= self._cfg.MEASURE_OFFSET

                for barline in measure_area_barlines:
                    if barline.x != 0:  # TODO Change to check if Barline location is not left
                        barline.x = int(x + max_measure_area)

                if measure_area.measure.has_irregular_rs_barline():
                    for irr_barline_label in measure_area_irr_barline_labels:
                        irr_barline_label.x = int(x + max_measure_area - irr_barline_label.content_width)
                        self.barline_shapes.append(irr_barline_label)
                    for irr_barline in measure_area_irr_barlines:
                        if irr_barline.x_start != 0:  # TODO Change to check if Barline location is not left
                            irr_barline.x_start = int(x + max_measure_area - irr_barline_label.content_width)
                            irr_barline.x_end = int(x + max_measure_area)

                self.barlines.extend(measure_area_barlines)
                self.irr_barlines.extend(measure_area_irr_barlines)
                self.irr_barline_labels.extend(measure_area_irr_barline_labels)

                self.slur_start_verts.append(measure_area_start_slurs)
                self.slur_end_verts.append(measure_area_end_slurs)
                self.tie_start_verts.append(measure_area_start_ties)
                self.tie_end_verts.append(measure_area_end_ties)

                self.measure_area_width.append(max_measure_area)
                x += max_measure_area
                self.score_width = x
                y = start_y

            for part in system.parts:
                y -= self._cfg.MEASURE_OFFSET
            self.score_height = y
            x = 0

    def _initialize_display_elements(self) -> None:
        self.background = pyglet.image.SolidColorImagePattern(
            # (255, 255, 255, 255)).create_image(self.width, self.height)
            (255, 255, 255, 255)).create_image(10000, 10000)
        self.load_labels(0, self.height - self._cfg.TOP_OFFSET, self.score.systems)

        num_parts = len(self.score.systems[0].parts)
        self.staff_lines = Staff(num_parts=num_parts, measure_widths=self.measure_area_width,
                                 height=self.height, batch=self.batch).staff_lines()
        self.ledger_lines = LedgerLine(ledger_coords=self.ledger_line_verts, batch=self.batch).ledger_lines()
        self._draw_beams()
        self._draw_stems()
        self._draw_slurs()
        self._draw_ties()
        self.draw_hairpins()
        self.draw_barlines()
        self.draw_irr_barlines()

    def draw_irr_barlines(self) -> None:
        used_barlines = list()
        for i in range(len(self.irr_barlines)):
            if i in used_barlines:
                continue

            x_start = self.irr_barlines[i].x_start
            x_end = self.irr_barlines[i].x_end
            y_bottom = self.irr_barlines[i].y_bottom
            y_top = self.irr_barlines[i].y_top
            for j in range(len(self.irr_barlines)):
                if j in used_barlines:
                    continue
                if (self.irr_barlines[j].measure == self.irr_barlines[i].measure and self.irr_barlines[
                    j].x_start == x_start):
                    y_bottom = self.irr_barlines[j].y_bottom
                    used_barlines.append(j)
            match self.irr_barlines[i].barlinetype:
                case BarlineType.RIGHT_REPEAT:
                    rectangle = shapes.Rectangle(x_start + ((x_end - x_start) * 2 / 3), y_top, (x_end - x_start) / 3,
                                                 y_bottom - y_top, color=_RGB_BLACK, batch=self.batch)
                    line = shapes.Line(x_start + (x_end - x_start) / 3 + 2, y_top, x_start + (x_end - x_start) / 3 + 2,
                                       y_bottom, width=4, color=_RGB_BLACK, batch=self.batch)
                    self.barline_shapes.append(rectangle)
                    self.barline_shapes.append(line)
                case BarlineType.FINAL:
                    rectangle = shapes.Rectangle(x_start + ((x_end - x_start) * 2 / 5) + 1, y_top,
                                                 ((x_end - x_start) * 3 / 5), y_bottom - y_top, color=_RGB_BLACK,
                                                 batch=self.batch)
                    line = shapes.Line(x_start + 1, y_top, x_start + 1, y_bottom, width=4, color=_RGB_BLACK,
                                       batch=self.batch)
                    self.barline_shapes.append(rectangle)
                    self.barline_shapes.append(line)
                # TODO add more cases for the different barline types

    def draw_barlines(self) -> None:
        used_barlines = list()

        for i in range(len(self.barlines)):
            if i in used_barlines:
                continue
            x = self.barlines[i].x
            y_bottom = self.barlines[i].y_bottom
            y_top = self.barlines[i].y_top
            for j in range(len(self.barlines)):
                if j in used_barlines:
                    continue
                if (self.barlines[j].measure == self.barlines[i].measure and self.barlines[j].x == x):
                    y_bottom = self.barlines[j].y_bottom
                    used_barlines.append(j)
            line = shapes.Line(x, y_top, x, y_bottom, width=2, color=_RGB_BLACK, batch=self.batch)
            self.barline_shapes.append(line)

    def on_draw(self, dt=None) -> None:
        self.clear()
        self.background.blit(-1 * (self.width // 2), -1 * (self.height // 2))

        self.camera_x += self.x_movement
        self.camera_y += self.y_movement
        self.view = self.view.from_translation(pyglet.math.Vec3(self.camera_x, self.camera_y, 0))
        # self._update_coordinates()

        self.batch.draw()
        if self.display_info:
            self.info_batch.draw()
        self.info_sprite.draw()
        # TODO I'm not sure what this line does or if it needs to be included.
        # pyglet.gl.glFlush()

    '''
    Creates info layout that displays score information when info sprite is clicked.
    '''

    def generate_info_layout(self):
        if not self.info_layout:
            title = self.score.metadata.title if self.score.metadata.title else '---'
            number = self.score.metadata.number if self.score.metadata.number else '---'
            composer = self.score.metadata.composer if self.score.metadata.composer else '---'
            work_title = self.score.metadata.work_title if self.score.metadata.work_title else '---'
            work_number = self.score.metadata.work_number if self.score.metadata.work_number else '---'
            opus_link = self.score.metadata.opus_link if self.score.metadata.opus_link else '---'
            source = self.score.metadata.source if self.score.metadata.source else '---'
            creators = '---'
            if self.score.metadata.creators:
                def join_tuple(str_tuple) -> str:
                    return ' '.join(str_tuple)

                temp = map(join_tuple, self.score.metadata.creators)
                creators = ', '.join(temp)
            rights = '---'
            if self.score.metadata.rights:
                def join_tuple(str_tuple) -> str:
                    return ' '.join(str_tuple)

                temp = map(join_tuple, self.score.metadata.rights)
                rights = ', '.join(temp)

            layout_text = f'Title: {title}\nNumber: {number}\nComposer: {composer}\nCreator(s): {creators}\nRights: ' \
                          f'{rights}\nSource: {source}\nWork Title: {work_title}\nWork Number: {work_number}\nOpus Link: {opus_link}'
            document = pyglet.text.document.FormattedDocument(layout_text)
            document.set_style(0, len(document.text), dict(font_name='Arial', font_size=16, color=(0, 0, 0, 255)))
            layout = pyglet.text.layout.TextLayout(document, 600, 100,
                                                   multiline=True, batch=self.info_batch)
            layout.x = 10
            layout.y = self.height - 150
            layout.anchor_y = 'top'
            self.info_layout = layout

    def display(self) -> None:
        pyglet.app.run()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        # stop screen movement when hovering info button
        if self.sprite_x1 < x < self.sprite_x2 and self.sprite_y1 < y < self.sprite_y2:
            self.x_movement = 0
            self.y_movement = 0
        else:
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
                       self.hairpin_lines, self.beam_lines, self.stems, self.slur_arcs, self.tie_arcs]

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

    '''
    Mouse click event handler
    Toggles display_info boolean if click is on info sprite
    '''

    def on_mouse_press(self, x, y, button, modifiers):
        sprite_x1 = self.info_sprite.x
        sprite_x2 = self.info_sprite.x + self.info_sprite.width
        sprite_y1 = self.info_sprite.y
        sprite_y2 = self.info_sprite.y + self.info_sprite.height
        if (sprite_x1 < x < sprite_x2) and (sprite_y1 < y < sprite_y2):
            self.display_info = not self.display_info
