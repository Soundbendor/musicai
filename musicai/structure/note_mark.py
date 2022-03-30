from enum import Enum
from typing import Union
import numpy as np
# todo: incorporate trills, mordants, etc.


class ArticulationType(Enum):
    """
    Represents most common articulation marks on notes
    """
    STACCATO = 0, u'\U0001D17C'  # Maybe problem: staccato changes are no constant
    STACCATISSIMO = 1, u'\U0001D17E'  # TODO: find the symbol for wedge
    ACCENT = 2, u'\U0001D17B'
    MARCATO = 3, 1, u'\U0001D17F'
    TENUTO = 4, 1, u'\U0001D17D'
    # FERMATA = 0, 0, u'\U0001D110'
    # ARPEGGIATO = 0, 0, u'\U0001D183'

    # -------------
    # Constructor
    # -------------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.symbol = values[1]  # symbol
        return obj

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls, abc_articulation):
        pass

        if abc_articulation == '.':
            return ArticulationType.STACCATO


class MiscMarks(Enum):
    """
    Represents miscellaneous marks on notes
    """
    FERMATA = 0, u'\U0001D110'
    FERMATA_SHORT = 1, ''  # TODO: need to find the symbol
    FERMATA_LONG = 2, ''
    ARPEGGIATO = 3, u'\U0001D183'
    ARPEGGIATO_DOWN = 4, u'\U0001D184'
    TIE = 5, ''

    # -------------
    # Constructor
    # -------------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.symbol = values[1]  # symbol
        return obj


# -----------------
# OrnamentType enum
# -----------------
class OrnamentType(Enum):
    TRILL = 0, '\U0001D196'
    UPPER_MORDANT = 1, '\U0001D19D'
    LOWER_MORDANT = 2
    TURN = 3, '\U0001D197'
    INVERTED_TURN = 4, '\U0001D198'
    TURN_SLASH = 4, '\U0001D199'
    TURN_UP = 4, '\U0001D19A'
    APPOGGIATURA = 5
    ACCIACCATURA = 6
    GLISSANDO = 7
    SLIDE = 8
    NACHSCHLAG = 9

    # TODO: Add tremolos


# class CustomArticulation:
#     """
#     Represents articulation types that use custom values
#     """
#     # -------------
#     # Constructor
#     # -------------
#     def __init__(self,
#                  articulation_type: ArticulationType = ArticulationType.ACCENT,
#                  force: Union[int, float, np.inexact, np.integer] = 1,
#                  length: Union[int, float, np.inexact, np.integer] = 1):
#         self.articulation_type = articulation_type
#         self.force = force
#         self.length = length


# -----------------
# GraceNoteMark class
# -----------------
class GraceNoteType(Enum):
    """
    Represents the two types of grace notes
    """
    ACCIACATURA = 0  # typical grace note
    APPOGGIATURA = 1


# -----------------
# GraceNoteMark class
# -----------------
class GraceNoteMark:  # What if they derive from some BASE class so that they can all have the same repr functions?
    """
    Class to represent grace notes
    """
    def __init__(self,
                 notes: Union[list, tuple] = None,
                 grace_note_type: GraceNoteType = GraceNoteType.ACCIACATURA):
        self.notes = list(notes)
        self.grace_note_type = grace_note_type


# -----------------
# NoteheadType enum
# -----------------
class NoteheadType(Enum):
    """
    Class to represent the shape of the notehead
    """
    ROUND = 0
    SQUARE = 1
    X = 1
    CIRCLE = 3
    PLUS = 3
    # DIAMOND
    #
    # TRIANGLE_RIGHT
    # TRIANGLE_LEFT
    #
    # TRIANGLE_UP
    #
    # MOON
    # TRIANGLE_ROUND
    # KEYSTONE
    # QUARTER_MOON
    # ISOSCELES_TRIANGLE
    #
    # MOON_LEFT
    # ARROWHEAD_LEFT
    # TRIANGLE_ROUND_LEFT

    # TODO ...


# -----------------
# NoteheadFill enum
# -----------------
class NoteheadFill(Enum):
    WHITE = 0
    BLACK = 1


# -------------
# StemType enum
# -------------
class StemType(Enum):
    DOWN = -1
    NONE = 0
    UP = 1
    DOUBLE = 2


# -------------
# BeamType enum
# -------------
class BeamType(Enum):
    NONE = 0
    BEGIN = 1
    CONTINUE = 2
    END = 3
    BACKWARD_HOOK = 4


# ----------
# Beam class
# ----------
class Beam:
    # -----------
    # Constructor
    # -----------
    def __init__(self, beamtype=BeamType.NONE, number=1):
        self.beamtype = beamtype
        self.number = number

    # --------
    # Override
    # --------
    def __str__(self):
        return self.beamtype.title()

    def __repr__(self):
        return '<{self.__class__.__name__}({self.beamtype.name}) num={self.number}>'.format(self=self)


# ------------
# TieType enum
# ------------
class TieType(Enum):
    STOP = 0
    START = 1


# --------------------
# TieLocationType enum
# --------------------
class TieLocationType(Enum):
    UNDER = 0
    OVER = 1


# ------------------
# DynamicChange enum
# ------------------
class DynamicChange(Enum):
    DIMINUENDO = -1
    DECRESCENDO = 0
    CRESCENDO = 1


# ------------------
# DynamicAccent enum
# ------------------
class DynamicAccent(Enum):
    POCOFORTE = 0, 'pf', u'\U0001D18F\U0001D191'
    FORTEPIANO = 1, 'fp', u'\U0001D191\U0001D18F'
    RINFORZANDO = 2, 'rf', u'\U0001D18C\U0001D191'

    FORZANDO = 3, 'fz', u'\U0001D191\U0001D18E'
    FORZATO = 4, 'fz', u'\U0001D191\U0001D18E'

    SFORZATO = 5, 'sf', u'\U0001D18D\U0001D191'
    SFORZANDO = 6, 'sfz', u'\U0001D18D\U0001D191\U0001D18E'

    # rfz, sffz, sfp, sfpp, sfz


# -------------
# Dynamic Class
# -------------
# class Dynamic:
#
#     # -----------
#     # Constructor
#     # -----------
#     def __init__(self, dynamic: Union[str, DynamicType]):
#         if isinstance(dynamic, DynamicType):
#             self.dynamic = dynamic
#         elif isinstance(dynamic, str):
#             pass
#
#         self.dynamic_accent = None
#
#         end_dynamic = self.dynamic


# ---------------------
# ArticulationType enum
# ---------------------
# class ArticulationType(Enum):
#     # Change in force, and length
#     STACCATO = 0, 0.5, u'\U0001D17C'
#     STACCATISSIMO = 1, 0.5, u'\U0001D17E'  # wedge
#     # SPICCATO = 1, 0.5, u'\U0001D17E'  # same as staccatissimo
#     ACCENT = 3, 0, 0.5, u'\U0001D17B'
#     MARCATO = 2, 0.5, u'\U0001D17F'
#     TENUTO = 3, 0.5, u'\U0001D17D'
#     # TENUTO_STACCATO = 3, 0.5, u'\U0001D182'
#     # MARCATO_STACCATO = 0, 0.5, u'\U0001D180'
#     # ACCENT_STACCATO = 0, 0.5, u'\U0001D181'
#     FERMATA = 0, 0, u'\U0001D110'
#     ARPEGGIATO = 0, 0, u'\U0001D183'
#
#     def __new__(cls, *values):
#         obj = object.__new__(cls)
#         # first value is canonical value
#         obj._value_ = values[1]  # a
#
#     # -------------
#     # Class Methods
#     # -------------
#     @classmethod
#     def from_abc(cls, abc_articulation):
#         pass
#
#         if abc_articulation == '.':
#             return ArticulationType.STACCATO


# --------------------
# BowArticulation enum
# --------------------
# class BowArticulation(Enum):
#     STOPPED, 'stopped note', 'left-hand pizzicato'
#     SNAP, 'snap pizzicato', 'Bartók pizzicato'
#     NATURAL, 'natural harmonic', 'flageolet'
#     UPBOW, 'up bow', 'sull\'arco','\U0001D1AB'
#     DOWNBOW, 'down bow', 'giù arco', '\U0001D1AA'


# ------------------
# Articulation class
# ------------------
class Articulation:
    pass





# --------------
# TrillType enum
# --------------
class TrillType(Enum):
    DIATONIC = 0
    CHROMATIC = 1


# ----------------
# Decoration class
# ----------------
class Decoration:
    pass



