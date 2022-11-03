import pyglet


class ScoreWindow(pyglet.window.Window):
    def __init__(self):
        super(ScoreWindow, self).__init__()

        self.background = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255)).create_image(self.width, self.height)

        pyglet.font.add_file('./assets/Bravura.otf')
        bravura = pyglet.font.load('Bravura')

        self.label = pyglet.text.Label(chr(int('F472', 16)),
                                       font_name='Bravura',
                                       font_size=36,
                                       x=self.width//2, y=self.height//2,
                                       anchor_x='center', anchor_y='center')
        self.label.color = (0, 0, 0, 255)

    def on_draw(self):
        self.clear()
        self.background.blit(0, 0)
        self.label.draw()


def main():
    """Main function"""
    window = ScoreWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
