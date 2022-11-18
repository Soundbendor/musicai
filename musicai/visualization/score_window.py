import pyglet
from pyglet import shapes


import json

from fileio.mxml import MusicXML
from visualization.view_area import MeasureArea


class ScoreWindow(pyglet.window.Window):
    def __init__(self, score):
        super(ScoreWindow, self).__init__()

        config = pyglet.gl.Config(
            sample_buffers=1, samples=8, double_buffer=False)

        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)

        pyglet.font.add_file('./visualization/assets/Bravura.otf')
        bravura = pyglet.font.load('Bravura')

        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name='Bravura',
                                       font_size=36,
                                       x=self.width//2, y=self.height//2,
                                       anchor_x='center', anchor_y='center')
        self.label.color = (0, 0, 0, 255)

        self.batch = pyglet.graphics.Batch()
        self.measures = []

        self.score = score

        # self.line = shapes.Line(
        #    100, 100, 50, 200, width = 19, color = (0, 0, 255), batch = self.batch)

    def draw_measure(self, x, y):
        line = shapes.Line(
            x, y, x + 100, y, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line)

        line2 = shapes.Line(
            x, y + 20, x + 100, y + 20, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line2)

        line3 = shapes.Line(
            x, y + 40, x + 100, y + 40, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line3)

        line4 = shapes.Line(
            x, y + 60, x + 100, y + 60, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line4)

        line5 = shapes.Line(
            x, y + 80, x + 100, y + 80, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line5)

        line6 = shapes.Line(
            x, y, x, y + 80, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line6)

        line7 = shapes.Line(
            x + 100, y, x + 100, y + 80, width=2, color=(0, 0, 0), batch=self.batch)
        self.measures.append(line7)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)

        self.x = 0
        self.y = 140 # Half of staff line drawing area

        for i in range(len(self.score.systems[0].parts[0].measures)):
            self.draw_measure(i * 100, 100)
        
        for system in self.score.systems:
            for part in system.parts:
                for measure in part.measures:
                    measure_area = MeasureArea(measure, self.x, self.y)
                    self.x += measure_area.area_width
                    measure_area.draw()

        self.batch.draw()
        pyglet.gl.glFlush()

        self.measures.clear()

    def display(self):
        pyglet.app.run()


def main():
    """Main function"""
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # score = MusicXML.load(file)
    # score.print_in_depth()

    window = ScoreWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
