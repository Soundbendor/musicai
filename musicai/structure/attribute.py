from enum import Enum
from typing import Union


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
class Beam():
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
    POCOFORTE = 0, 'pf', '\U0001D18F\U0001D191'
    FORTEPIANO = 1, 'fp', '\U0001D191\U0001D18F'
    RINFORZANDO = 2, 'rf', '\U0001D18C\U0001D191'

    FORZANDO = 3, 'fz', '\U0001D191\U0001D18E'
    FORZATO = 4, 'fz', '\U0001D191\U0001D18E'

    SFORZATO = 5, 'sf', '\U0001D18D\U0001D191'
    SFORZANDO = 6, 'sfz', '\U0001D18D\U0001D191\U0001D18E'

    # rfz, sffz, sfp, sfpp, sfz


# ----------------
# DynamicType enum
# ----------------
class DynamicType(Enum):
    NONE = 0, 0, '', ''
    PIANISSISSISSIMO = 1, 10, 'pppp', '\U0001D18F\U0001D18F\U0001D18F\U0001D18F'
    PIANISSISSIMO = 2, 23, 'ppp', '\U0001D18F\U0001D18F\U0001D18F'
    PIANISSIMO = 3, 36, 'pp', '\U0001D18F\U0001D18F'
    PIANO = 4, 49, 'p', '\U0001D18F'
    MEZZOPIANO = 5, 62, 'mp', '\U0001D190\U0001D18F'
    MEZZOFORTE = 6, 75, 'mf', '\U0001D190\U0001D191'
    FORTE = 7, 88, 'f', '\U0001D191'
    FORTISSIMO = 8, 101, 'ff', '\U0001D191\U0001D191'
    FORTISSISSIMO = 9, 114, 'fff', '\U0001D191\U0001D191\U0001D191'
    FORTISSISSISSIMO = 10, 127, 'ffff', '\U0001D191\U0001D191\U0001D191\U0001D191'

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.velocity = values[1]
        obj.abbr = values[2]
        obj.symbol = values[3]
        obj._all_values = values
        return obj


# -------------
# Dynamic Class
# -------------
class Dynamic:

    # -----------
    # Constructor
    # -----------
    def __init__(self, dynamic: Union[str, DynamicType]):
        if isinstance(dynamic, DynamicType):
            self.dynamic = dynamic
        elif isinstance(dynamic, str):
            pass

        self.dynamic_accent = None

        end_dynamic = self.dynamic


# ---------------------
# ArticulationType enum
# ---------------------
class ArticulationType(Enum):
    # TODO: fix numbers
    STACCATO = 0, 0.5, '\U0001D17C'
    STACCATISSIMO = 1, 0.5, '\U0001D17E'
    SPICCATO = 1, 0.5, '\U0001D17E'  # same as staccatissimo
    ACCENT = 3, 0, 0.5, '\U0001D17B'
    MARCATO = 2, 0.5, '\U0001D17F'
    TENUTO = 3, 0.5, '\U0001D17D'
    TENUTO_STACCATO = 3, 0.5, '\U0001D182'
    MARCATO_STACCATO = 0, 0.5, '\U0001D180'
    ACCENT_STACCATO = 0, 0.5, '\U0001D181'

    # TODO fermata? up/down

    # TODO CRESCENDO?

    # TODO override __new__

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def from_abc(cls, abc_articulation):
        pass

        if abc_articulation == '.':
            return ArticulationType.STACCATO


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
