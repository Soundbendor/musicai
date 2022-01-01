
# ----------
# Part class
# ----------
class Part:
    """
    Class to represent a Part
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.measures = []

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for measure in self.measures:
            if measure is None:
                raise ValueError('measure is None')
            ret_str += '' + str(measure) + ' '
        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, measure):
        self.measures.append(measure)

# ----------------
# PartSystem class
# ----------------
class PartSystem:
    """
    Class to represent a Part System
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.parts = []

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for part in self.parts:
            if part is None:
                #  ValueError('Part is None')
                pass
            ret_str += '' + str(part) + '\n'
        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, part):
        self.parts.append(part)

# ----------
# Work class
# ----------
class Work():
    """
    Class to represent a Work
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.title = ''
        self.number = 0
        self.composer = ''

# -----------
# Score class
# -----------
class Score():
    """
    Class to represent a Score
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.filename = ''
        self.systems = []
        self.number = 0
        self.title = []
        self.composer = ''

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for system in self.systems:
            if system is None:
                raise ValueError('system is None')
            ret_str += '' + str(system) + ' '
        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, system):
        self.systems.append(system)


def get_test_score():
    from musicai.structure.note import Note, NoteType
    from musicai.structure.pitch import Pitch, Step
    from musicai.structure.measure import Measure
    from musicai.structure.score import Part, PartSystem
    from musicai.structure.clef import Clef
    from musicai.structure.key import Key, KeyType, ModeType

    n1 = Note(value=NoteType.EIGHTH, pitch=Pitch('A3'))
    n2 = Note(value=NoteType.EIGHTH, pitch=Pitch('B3'))
    n3 = Note(value=NoteType.EIGHTH, pitch=Pitch('C4'))
    n4 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('D4'))
    n5 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('E4'))
    n6 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('G5'))
    n7 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('A5'))
    n8 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('B5'))
    n9 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('C6'))

    m1 = Measure()

    m1.clef = Clef()  # treble
    #m1.clef = Clef(ClefType.BASS)
    #m1.key = Key()     # CMaj

    m1.key = Key(keytype=KeyType.Bb, modetype=ModeType.MAJOR)  # CMaj
    m1.append([n1, n2, n3, n4, n5, n6, n7, n8, n9])
    m1.set_accidentals()

    p1 = Part()
    p1.append(m1)

    s1 = PartSystem()
    s1.append(p1)

    score = Score()
    score.append(s1)


    return score