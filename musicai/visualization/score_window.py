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
        super(ScoreWindow, self).__init__()

        config = pyglet.gl.Config(
            sample_buffers=1, samples=8, double_buffer=False)
        self.msvcfg = WindowConfig()
        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)

        pyglet.font.add_file('./visualization/assets/Bravura.otf')
        bravura = pyglet.font.load(self.msvcfg.MUSIC_FONT_NAME)

        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name=self.msvcfg.MUSIC_FONT_NAME,
                                       font_size=int(self.msvcfg.MUSIC_FONT_SIZE),
                                       x=self.width // 2, y=self.height // 2,
                                       anchor_x='center', anchor_y='center')
        self.label.color = (0, 0, 0, 255)

        self.batch = pyglet.graphics.Batch()
        self.measures = []
        self.barlines = []

        self.score = score

        self.labels = []
        self.measure_height = 80

        self.load_labels(0, 100)
        # self.load_measure_one(0, 100)

        # self.line = shapes.Line(
        #    100, 100, 50, 200, width = 19, color = (0, 0, 255), batch = self.batch)

        self.initialize_display_elements()
        self.x_movement = 0
        self.y_movement = 0

    def draw_measure(self, x, y):
        zoom = 1    # zoom size: integrate keyboard/mouse scrolling to edit. Also make class variable

        spacing = 20

        staff = []
        for i in range(5):
            staff.append(shapes.Line(
                x, y + i * (spacing * zoom), (x + 100) * zoom, y + i * (spacing * zoom), width=2, color=(0, 0, 0), batch=self.batch))
            self.measures.append(staff[i])

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
                y -= 200

    def initialize_display_elements(self):
        for i in range(len(self.score.systems[0].parts[0].measures)):
            self.draw_measure(i * 100, 100)

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

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)
        self.update_x()
        self.update_y()
        self.batch.draw()
        pyglet.gl.glFlush()

        # self.measures.clear()
        # self.barlines.clear()
        # barline_shapes.clear()

    def display(self):
        pyglet.app.run()

    def on_mouse_motion(self, x, y, dx, dy):
        if _DEBUG:
            print(f"on_mouse_motion")

    def on_mouse_leave(self, x, y):
        if _DEBUG:
            print(f"on_mouse_leave")
            print(f"mouse has left the screen")

    def update_x(self):
        for label, measure in zip(self.labels, self.measures):
            label.x += self.x_movement
            measure.x += self.x_movement

    def update_y(self):
        for label, measure in zip(self.labels, self.measures):
            label.y += self.y_movement
            measure.y += self.y_movement

    def on_key_press(self, symbol, modifiers):
        if _DEBUG:
            print(f"on_key_press, symbol: {symbol}, modifiers: {modifiers}")

        match str(symbol):
            case self.msvcfg.KEYBIND_UP:
                if _DEBUG:
                    print(f"up key pressed: {symbol}")
                self.y_movement = -1 * int(self.msvcfg.FAST_MOVEMENT)
                # for label in self.labels:
                #     label.y -= int(self.msvcfg.FAST_MOVEMENT)

            case self.msvcfg.KEYBIND_DOWN:
                if _DEBUG:
                    print(f"down key pressed: {symbol}")
                self.y_movement = int(self.msvcfg.FAST_MOVEMENT)

            case self.msvcfg.KEYBIND_LEFT:
                if _DEBUG:
                    print(f"left key pressed: {symbol}")
                self.x_movement = int(self.msvcfg.FAST_MOVEMENT)

            case self.msvcfg.KEYBIND_RIGHT:
                if _DEBUG:
                    print(f"right key pressed: {symbol}")
                self.x_movement = -1 * int(self.msvcfg.FAST_MOVEMENT)

            case self.msvcfg.KEYBIND_EXIT:
                if _DEBUG:
                    print(f"escape pressed: {symbol}")
                self.close()
            case _:
                if _DEBUG:
                    print(f"other key pressed")

    def on_key_release(self, symbol, modifiers):
        if _DEBUG:
            print(f"on_key_release, symbol: {symbol}, modifiers: {modifiers}")
        match str(symbol):
            case self.msvcfg.KEYBIND_UP:
                if _DEBUG:
                    print(f"up key released: {symbol}")
                self.y_movement = 0
            case self.msvcfg.KEYBIND_DOWN:
                if _DEBUG:
                    print(f"down key released: {symbol}")
                self.y_movement = 0
            case self.msvcfg.KEYBIND_LEFT:
                if _DEBUG:
                    print(f"left key released: {symbol}")
                self.x_movement = 0
            case self.msvcfg.KEYBIND_RIGHT:
                if _DEBUG:
                    print(f"right key released: {symbol}")
                self.x_movement = 0
            case _:
                if _DEBUG:
                    print(f"other key released")


def main():
    """Main function"""
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # score = MusicXML.load(file)
    # score.print_in_depth()

    window = ScoreWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
