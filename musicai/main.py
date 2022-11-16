import pyglet

#from fileio import MusicXML
from visualization.score_window import ScoreWindow
from fileio.mxml import MusicXML


def main():
    print('main module')

    file = '../examples/mxml/MozartTrio.musicxml'
    score = MusicXML.load(file)

    window = ScoreWindow(score)
    window.display()


if __name__ == "__main__":
    main()
