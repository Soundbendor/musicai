import operator
import unittest
from musicai.structure.score import Part, PartSystem, Score


# Depreceated
def get_test_score() -> Score:
    from musicai.structure.note import Note, NoteType, NoteValue
    from musicai.structure.pitch import Pitch
    from musicai.structure.measure import Measure
    from musicai.structure.score import Part, PartSystem, Score
    from musicai.structure.clef import Clef
    from musicai.structure.key import Key, KeyType, ModeType

    n1 = Note(value=NoteValue(NoteType.EIGHTH), pitch=Pitch('A3'))
    n2 = Note(value=NoteValue(NoteType.EIGHTH), pitch=Pitch('B3'))
    n3 = Note(value=NoteValue(NoteType.EIGHTH), pitch=Pitch('C4'))
    n4 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('D4'))
    n5 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('E4'))
    n6 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('G5'))
    n7 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('A5'))
    n8 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('B5'))
    n9 = Note(value=NoteValue(NoteType.SIXTEENTH), pitch=Pitch('C6'))

    m1 = Measure()

    m1.clef = Clef()  # treble
    # m1.clef = Clef(ClefType.BASS)
    # m1.key = Key()     # CMaj

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
