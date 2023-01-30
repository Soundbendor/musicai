import pyglet

#from fileio import MusicXML
from visualization.score_window import ScoreWindow
from fileio.mxml import MusicXML


def main():
    print('main module')

    # ---- Only one that looks decent ----
    file = '../examples/mxml/MozartTrio.musicxml'

    # ---- Viewable musicxml files ----
    #file = '../examples/mxml/BrahWiMeSample.musicxml'
    #file = '../examples/mxml/Dichterliebe01.musicxml'
    #file = '../examples/mxml/MahlFaGe4Sample.musicxml'
    #file = '../examples/mxml/MozaChloSample.musicxml'
    #file = '../examples/mxml/Telemann.musicxml'

    # ---- Non-working musicxml files ----
    #file = '../examples/mxml/ActorPreludeSample.musicxml'      # Chord problem?
    #file = '../examples/mxml/BeetAnGeSample.musicxml'          # Glyph noteUp not found in font in view_area.py
    #file = '../examples/mxml/Binchois.musicxml'                # Issue with mxml parser
    #file = '../examples/mxml/BrookeWestSample.musicxml'        # Issue with mxml parser
    #file = '../examples/mxml/Chant.musicxml'                   # Issue with mxml parser
    #file = '../examples/mxml/DebuMandSample.musicxml'          # Issue with mxml parser
    #file = '../examples/mxml/Echigo-Jishi.musicxml'            # self.barlines issue in score_window.py
    #file = '../examples/mxml/FaurReveSample.musicxml'          # Issue in mxml parser
    #file = '../examples/mxml/HelloWorld.musicxml'              # Glyph noteWholeUp note found in font in view_area.py
    #file = '../examples/mxml/MozartPianoSonata.musicxml'       # Issue with mxml parser
    #file = '../examples/mxml/MozaVeilSample.musicxml'          # Glyph noteUp not found in font in view_area.py
    #file = '../examples/mxml/Saltarello.musicxml'              # self.barlines issue in score_window.py 
    #file = '../examples/mxml/SchbAvMaSample.musicxml'          # Glyph noteUp not found in font in view_area.py

    # ---- Non-working mxl files ---- (Not supported in mxml parser)
    #file = '../examples/mxml/ActorPreludeSample.mxl'      
    #file = '../examples/mxml/BeetAnGeSample.mxl'          
    #file = '../examples/mxml/Binchois.mxl'                
    #file = '../examples/mxml/BrookeWestSample.mxl'        
    #file = '../examples/mxml/Chant.mxl'                   
    #file = '../examples/mxml/DebuMandSample.mxl'          
    #file = '../examples/mxml/Echigo-Jishi.mxl'            
    #file = '../examples/mxml/FaurReveSample.mxl'                      
    #file = '../examples/mxml/MozartPianoSonata.mxl'       
    #file = '../examples/mxml/MozaVeilSample.mxl'          
    #file = '../examples/mxml/Saltarello.mxl'              
    #file = '../examples/mxml/SchbAvMaSample.mxl'          


    score = MusicXML.load(file)

    # ------Slicing to one part and 3 measures to work with something small
    # score = score[0:4]
    # score = score.slice_parts(0,1)

    window = ScoreWindow(score)
    window.display()


if __name__ == "__main__":
    main()
