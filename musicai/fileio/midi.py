#MIDI to MusicAI parser
# Soundbendor Lab, dev: Scot Rein

import numpy as np

from musicai.structure.note_mark import StemType, Beam, BeamType, TieType, ArticulationType, OrnamentType, SlurType, \
    NoteheadType, Notehead
from musicai.structure.clef import Clef, ClefOctave, ClefType
from musicai.structure.key import ModeType, KeyType, Key
from musicai.structure.lyric import Lyric, SyllabicType
from musicai.structure.measure import Measure, Barline, BarlineType, BarlineLocation, Transposition
from musicai.structure.measure_mark import MeasureMark, InstantaneousMeasureMark, DynamicMark, DynamicType
from musicai.structure.note import NoteType, Ratio, NoteValue, Rest, Note, NoteGroup
from musicai.structure.pitch import Accidental, Pitch, Octave, Step
from musicai.structure.score import Score, PartSystem, Part, GroupingSymbol
from musicai.structure.time import TimeSignature, TimeSymbolType, Tempo


class MidiConversion():

    @staticmethod
    def load(midi_filepath: str) -> Score:
        pass

    @staticmethod
    def save():
        pass





