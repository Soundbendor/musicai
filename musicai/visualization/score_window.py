import pyglet


class ScoreWindow(pyglet.window.Window):
    def __init__(self):
        super(ScoreWindow, self).__init__()

        self.label = pyglet.text.Label('Hello, world',
                                       font_name='Times New Roman',
                                       font_size=36,
                                       x=self.width//2, y=self.height//2,
                                       anchor_x='center', anchor_y='center')

    def on_draw(self):
        self.clear()
        self.label.draw()


def main():
    """Main function"""
    window = ScoreWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
