import pyglet

#from fileio import MusicXML
from visualization.score_window import ScoreWindow
from fileio.mxml import MusicXML
from visualization.window_config import WindowConfig


def main():
    print('main module')

    file = '../examples/mxml/MozartTrio.musicxml'
    score = MusicXML.load(file)

    # ------Slicing to one part and 3 measures to work with something small
    # score = score[0:4]
    # score = score.slice_parts(0,1)

    window = ScoreWindow(score)
    window.display()


if __name__ == "__main__":
    main()
