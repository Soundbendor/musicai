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
        bravura = pyglet.font.load('Bravura')

        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name='Bravura',
                                       font_size=36,
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
            for part in system.parts:
                for idx, measure in enumerate(part.measures):
                    measure_area = MeasureArea(
                        measure, x, y, self.measure_height, idx)
                    # TODO calc and set area_width
                    x += measure_area.area_width
                    measure_labels = measure_area.get_labels()
                    for label in measure_labels:
                        label.batch = self.batch
                        self.labels.append(label)
                    barline_verts = measure_area.get_barlines()
                    for vert in barline_verts:
                        self.barlines.append(vert)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)

        for i in range(len(self.score.systems[0].parts[0].measures)):
            self.draw_measure(i * 100, 100)

        barline_shapes = []
        for vert in self.barlines:
            line = shapes.Line(vert[0], vert[1], vert[2], vert[3], width=2, color=(
                0, 0, 0), batch=self.batch)
            barline_shapes.append(line)

        self.batch.draw()
        pyglet.gl.glFlush()

        self.measures.clear()
        # self.barlines.clear()
        barline_shapes.clear()

    def display(self):
        pyglet.app.run()

    def on_mouse_motion(self, x, y, dx, dy):
        if _DEBUG:
            print(f"on_mouse_motion")

    def on_mouse_leave(self, x, y):
        if _DEBUG:
            print(f"on_mouse_leave")
            print(f"mouse has left the screen")

    def on_key_press(self, symbol, modifiers):
        if _DEBUG:
            print(f"on_key_press, symbol: {symbol}, modifiers: {modifiers}")

        match str(symbol):
            case self.msvcfg.KEYBIND_UP:
                if _DEBUG:
                    print(f"up key pressed: {symbol}")
            case self.msvcfg.KEYBIND_DOWN:
                if _DEBUG:
                    print(f"down key pressed: {symbol}")
            case self.msvcfg.KEYBIND_LEFT:
                if _DEBUG:
                    print(f"left key pressed: {symbol}")
            case self.msvcfg.KEYBIND_RIGHT:
                if _DEBUG:
                    print(f"right key pressed: {symbol}")
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
            case self.msvcfg.KEYBIND_DOWN:
                if _DEBUG:
                    print(f"down key released: {symbol}")
            case self.msvcfg.KEYBIND_LEFT:
                if _DEBUG:
                    print(f"left key released: {symbol}")
            case self.msvcfg.KEYBIND_RIGHT:
                if _DEBUG:
                    print(f"right key released: {symbol}")
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
