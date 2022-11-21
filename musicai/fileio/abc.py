# ABC to MusicAI parser
# Soundbendor Lab, dev: Scot Rein

import re

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


class AbcConversion():

    @classmethod
    def parse_abc_line(line):
        pass
        # switch case regex matches for all possible line types
        # basic line types are parsed instantly (header, written)
        # notaion lines have measures extracted via regex group matches, parsed individually


    @classmethod
    def parse_abc_measure(measure):
        pass


    @staticmethod
    def load(abc_filepath: str) -> Score:
        # Place file into workable structure before parsing
        with open(abc_filepath) as abc_file:
            file_lines = abc_file.readlines()


    @staticmethod
    def save():
        pass












