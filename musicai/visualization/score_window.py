import pyglet
from pyglet import shapes
from pyglet.window import key

import json

from fileio.mxml import MusicXML
from visualization.view_area import MeasureArea
from visualization.window_config import WindowConfig

_DEBUG = True


class ScoreWindow(pyglet.window.Window):
    def __init__(self, score):
        self.msvcfg = WindowConfig()
        super(ScoreWindow, self).__init__(height=self.msvcfg.SCREEN_HEIGHT, width=self.msvcfg.SCREEN_WIDTH)

        # TODO: Is this variable used at all?
        config = pyglet.gl.Config(
            sample_buffers=1, samples=8, double_buffer=False)

        pyglet.font.add_file(self.msvcfg.MUSIC_FONT_FILE)
        bravura = pyglet.font.load(self.msvcfg.MUSIC_FONT_NAME)

        # TODO: What does label do and do we need it?
        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name=self.msvcfg.MUSIC_FONT_NAME,
                                       font_size=int(self.msvcfg.MUSIC_FONT_SIZE),
                                       x=self.width // 2, y=self.height // 2,
                                       anchor_x='center', anchor_y='center')
        self.label.color = (0, 0, 0, 255)

        self.batch = pyglet.graphics.Batch()
        self.measures = []
        self.barlines = []
        self.barline_shapes = []

        self.score = score

        self.labels = []
        self.measure_height = int(self.msvcfg.MEASURE_HEIGHT)
        self.measure_area_width = []

        # self.load_measure_one(0, 100)

        # self.line = shapes.Line(
        #    100, 100, 50, 200, width = 19, color = (0, 0, 255), batch = self.batch)

        self.initialize_display_elements()
        self.x_movement = 0
        self.y_movement = 0

    def draw_measure(self, x_start, measure_length, y):
    # def draw_measure(self, x, y):

        zoom = 1    # zoom size: integrate keyboard/mouse scrolling to edit. Also make class variable

        spacing = 20

        staff = []
        for i in range(5):
            # bar_line = shapes.Line(0, y + i * (spacing * zoom), x * zoom, y + i * (spacing * zoom), width=2, color=(0, 0, 0), batch=self.batch)
            bar_line = shapes.Line(x_start, y + i * (spacing * zoom), (x_start + measure_length) * zoom, y + i * (spacing * zoom), width=2, color=(0, 0, 0), batch=self.batch)
            staff.append(bar_line)
            self.measures.append(staff[i])

    # TODO: Do we want each measure length to be a separate segment?
    # The code listed here can be adapted to draw as a whole line, or as separate segments
    def draw_measures(self):
        # total_width = sum(self.measure_area_width)
        # print(f"total_width: {total_width}")
        for num_parts in range(len(self.score.systems[0].parts)):
            total_width = 0
            # self.draw_measure(total_width, self.height - self.msvcfg.TOP_OFFSET - (num_parts * 200))
            for num_measures in range(len(self.score.systems[0].parts[0].measures)):
                measure_width = self.measure_area_width[num_measures]
                self.draw_measure(total_width, measure_width ,self.height - self.msvcfg.TOP_OFFSET - (num_parts * self.msvcfg.MEASURE_OFFSET))
                total_width += measure_width

    def load_barlines(self, measure_area):
        verts = measure_area.get_barlines()
        self.barlines.append(verts)

    def load_labels(self, x, y):
        for system in self.score.systems:
            measure_area_width = []
            for i in range(len(system.parts[0].measures)):
                max_measure_area = 0
                for part in system.parts:
                    measure_area = MeasureArea(part.measures[i], x, y, self.measure_height, i)
                    if (measure_area.area_width > max_measure_area):
                        max_measure_area = measure_area.area_width
                measure_area_width.append(int(max_measure_area))

            for part in system.parts:
                for idx, measure in enumerate(part.measures):
                    measure_area = MeasureArea(measure, x, y, self.measure_height, idx)
                    # TODO calc and set area_width
                    # x += measure_area.area_width
                    x += measure_area_width[idx]
                    measure_labels = measure_area.get_labels()
                    for label in measure_labels:
                        label.batch = self.batch
                        self.labels.append(label)
                    barline_verts = measure_area.get_barlines()
                    for vert in barline_verts:
                        self.barlines.append(vert)
                x = 0
                y -= self.msvcfg.MEASURE_OFFSET
        self.measure_area_width = measure_area_width

    def initialize_display_elements(self):
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)
        self.load_labels(0, self.height - int(self.msvcfg.TOP_OFFSET))
        self.draw_measures()

        barline_shapes = []

        for i in range(len(self.score.systems[0].parts[0].measures)):
            x = self.barlines[i][0]
            y_start = self.barlines[i][1]
            y_end = self.barlines[i][3]

            for vert in self.barlines:
                if vert[0] == x:
                    y_start = vert[1]
            line = shapes.Line(x, y_start, x, y_end, width=2, color=(0, 0, 0), batch=self.batch)
            barline_shapes.append(line)
        self.barline_shapes = barline_shapes

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)

        self.update_x()
        self.update_y()

        self.batch.draw()
        # TODO I'm not sure what this line does or if it needs to be included.
        # pyglet.gl.glFlush()



    def display(self):
        pyglet.app.run()

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_leave(self, x, y):
        pass

    def update_x(self):
        for label in self.labels:
            label.x += self.x_movement
        for measure in self.measures:
            measure.x += self.x_movement
        for barline_shape in self.barline_shapes:
            barline_shape.x += self.x_movement

    def update_y(self):
        for label in self.labels:
            label.y += self.y_movement
        for measure in self.measures:
            measure.y += self.y_movement
        for barline_shape in self.barline_shapes:
            barline_shape.y += self.y_movement

    def on_key_press(self, symbol, modifiers):
        if _DEBUG:
            print(f"on_key_press, symbol: {symbol}, modifiers: {modifiers}")

        match symbol:
            case self.msvcfg.KEYBIND_UP:
                if _DEBUG:
                    print(f"up key pressed: {symbol}")
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
                if _DEBUG:
                    print(f"other key pressed")
                pass

    def on_key_release(self, symbol, modifiers):
        if _DEBUG:
            print(f"on_key_release, symbol: {symbol}, modifiers: {modifiers}")
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


def main():
    """Main function"""
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # score = MusicXML.load(file)
    # score.print_in_depth()

    window = ScoreWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
