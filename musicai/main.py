import pyglet

#from fileio import MusicXML
from visualization.score_window import ScoreWindow
from visualization.window_config import WindowConfig
from fileio.mxml import MusicXML


def main():
    print('main module')

    # ---- Decent looking ./mxml scores ----
    #file = '../examples/mxml/MozartTrio.musicxml'

    # ---- Decent looking ./mxml2 scores ----
    #file = '../examples/mxml2/Bach_Cello_Suite_No._1_For_Violin.musicxml'
    file = '../examples/mxml2/Prelude_No._3_BWV_848_in_C_Major.musicxml'

    # ---- Viewable (Buggy) ./mxml files ----
    #file = '../examples/mxml/BrahWiMeSample.musicxml'
    #file = '../examples/mxml/Dichterliebe01.musicxml'
    #file = '../examples/mxml/MahlFaGe4Sample.musicxml'
    #file = '../examples/mxml/MozaChloSample.musicxml'
    #file = '../examples/mxml/Telemann.musicxml'

    # ---- Viewable (Buggy) ./mxml2 files ----
    # file = '../examples/mxml2/Dance_of_the_Sugar_Plum_Fairy.musicxml'  # Second part has no staff

    # ---- Non-working ./mxml files ----
    # file = '../examples/mxml/ActorPreludeSample.musicxml'          # Chord problem?
    # file = '../examples/mxml/BeetAnGeSample.musicxml'              # Glyph noteUp not found in font in view_area.py
    # file = '../examples/mxml/Binchois.musicxml'                    # Issue with mxml parser
    # file = '../examples/mxml/BrookeWestSample.musicxml'            # Issue with mxml parser
    # file = '../examples/mxml/Chant.musicxml'                       # Issue with mxml parser
    # file = '../examples/mxml/DebuMandSample.musicxml'              # Issue with mxml parser
    # file = '../examples/mxml/Echigo-Jishi.musicxml'                # self.barlines issue in score_window.py
    # file = '../examples/mxml/FaurReveSample.musicxml'              # Issue in mxml parser
    # file = '../examples/mxml/HelloWorld.musicxml'                  # Glyph noteWholeUp note found in font in view_area.py
    # file = '../examples/mxml/MozartPianoSonata.musicxml'           # Issue with mxml parser
    # file = '../examples/mxml/MozaVeilSample.musicxml'              # Glyph noteUp not found in font in view_area.py
    # file = '../examples/mxml/Saltarello.musicxml'                  # self.barlines issue in score_window.py
    # file = '../examples/mxml/SchbAvMaSample.musicxml'              # Glyph noteUp not found in font in view_area.py

    # ---- Non-working ./mxml2 files ----
    # file = '../examples/mxml2/Canon_in_D__Violin_Solo_.musicxml'           # Glyph notwWholeUp not found in view_area.py
    # file = '../examples/mxml2/Cello_Scale_2_Octaves.musicxml'              # KeyError 'NoneMajor' (C Major/A Minor) in mxml parser
    # file = '../examples/mxml2/J.S.Bach_-_Suite_no._4_for_Cello_solo_BWV_1010.musicxml'     # Index out of range in score_window.py
    # file = '../examples/mxml2/Major_and_Minor_Scales_violin.musicxml'      # Glyph noteWholeUp not found in view_area.py
    # file = '../examples/mxml2/Piano_Concerto_in_A_minor_Opus_16_Grieg_1st_Movement_-_Allegro_molto_moderato.musicxml' # Type fp not yet supported in mxml parser
    # file = '../examples/mxml2/Prelude_Opus_3_No._2_in_C_Minor.musicxml'    # Many errors. Glyph noteWholeUp not found in view_area.py
    # file = '../examples/mxml2/Rigadoon.musicxml'                           # Time and Key should already be set in mxml parser
    # file = '../examples/mxml2/Spring-Four_seasons_vivaldi.musicxml'        # Glyph wholeNoteUp not found in view_area.py
    # file = '../examples/mxml2/Tarantella_in_D_Minor.musicxml'              # Dynamic Type fp not supported in mxml parser
    # file = '../examples/mxml2/Mozart_Symphony_No._40_in_G_Minor_K._550_I._Molto_Allegro.musicxml'  # Dynamic Type sf not supported in mxml parser
    # file = '../examples/mxml2/Symphony_No._5_1st_Movement.musicxml'        # Dynamic Type other-dynamics not supported in mxml parser
    # file = '../examples/mxml2/Canon_in_D_-_Violin_Cello.musicxml'          # Glyph noteWholeUp not found in view_area.py
    # file = '../examples/mxml2/Mozart_-_Symphony_No.40_in_G_minor_K.550_Movement_1.musicxml'   # Glyph noteWholeUp not found in view_area.py

    score = MusicXML.load(file)

    # ------Slicing to one part and 3 measures to work with something small
    # score = score[0:4]
    # score = score.slice_parts(0,1)

    window = ScoreWindow(score, WindowConfig())
    window.display()


if __name__ == "__main__":
    main()
