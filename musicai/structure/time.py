import warnings
from enum import Enum
from typing import Union
import numpy as np


# -------------------
# TimeSymbolType enum
# -------------------
class TimeSymbolType(Enum):
    """
     Class to represent the type of a time signature
     """
    NORMAL = 0
    COMMON = 1
    CUT = 2
    SINGLE = 3
    # SENZA_MISURA = 4

    # --------
    # Override
    # --------
    def __str__(self):
        return f'{self.name}'.lower()

    def __repr__(self):
        return f'{self.name}({self.value})'


# ---------------
# TimeSymbol enum
# ---------------
class TimeSignature:
    """
    Class to represent a musical time signature
    """

    # -----------
    # Constructor
    # -----------
    def __init__(self, numerator=4, denominator=4, timesymboltype=TimeSymbolType.NORMAL):
        self.numerator = numerator
        self.denominator = denominator
        self.timesymboltype = timesymboltype
        self.divisions = 0
        # override
        if timesymboltype == TimeSymbolType.COMMON:
            self.numerator = 4
            self.denominator = 4
        elif timesymboltype == TimeSymbolType.CUT:
            self.numerator = 2
            self.denominator = 2

    # ----------
    # Properties
    # ----------
    @property
    def value(self):
        return self.numerator / self.denominator

    # --------
    # Override
    # --------
    def __str__(self):
        return str(self.numerator) + '/' + str(self.denominator)

    def __repr__(self):
        return '<TimeSignature: ' + str(self.numerator) + '/' + str(self.denominator) \
               + '; ' + self.timesymboltype.__repr__() + '>'

    # -------------
    # Methods
    # -------------
    def is_equivilant(self, other: 'TimeSignature') -> bool:
        """
        Tells whether this is notationally equivilant to another Time Signature. This is based on the numerator and
        denominator

        :param other: The other Time Signature to compare to the current one
        :return: Bool describing if they are notationally equivilant or not. Based on numerator and
        denominator
        """
        if isinstance(other, TimeSignature):
            if self.numerator == other.numerator and self.denominator == other.denominator:
                return True
            else:
                return False

        else:
            return False

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def find(cls, time) -> 'TimeSignature':
        # C| cut
        if time.__contains__('\\'):
            # e.g., 4/4 or 6/8
            words = time.split('\\')
            return TimeSignature(words[0], words[1])
        elif time == 'C':
            # common time
            return TimeSignature(numerator=4, denominator=4, timesymboltype=TimeSymbolType.COMMON)
        elif time == 'C|':
            # cut time
            return TimeSignature(numerator=2, denominator= 2, timesymboltype=TimeSymbolType.CUT)
        else:
            raise ValueError(f'Cannot find TimeSignature for {time}.')


# -------------------
# TempoType enum
# -------------------
class TempoType(Enum):
    """
    Enum to represent different standard tempo markings, with tempo approximations for 4/4 time
    """
    NONE = 0, 0, 0, ''
    LARGHISSIMO = 1, 24, 12.5, 'very, very slow'
    ADAGISSIMO = 24, 40, 32, 'very slow'
    GRAVE = 25, 45, 35, 'very slow'
    LARGO = 40, 60, 50, 'slow and broad'
    LENTO = 45, 60, 52.5, 'slow'
    LARGHETTO = 60, 66, 63, 'rather slow and broad'
    ADAGIO = 66, 76, 71, 'slow with great expression'
    ADAGIETTO = 70, 80, 75, 'rather slow'
    ANDANTE = 76, 108, 92, 'at a walking pace'
    ANDANTINO = 80, 108, 94, 'slightly faster than andante'
    MARCIA_MODERATOR = 83, 85, 84, 'moderately, in a manner of a march'
    MODERATO = 108, 120, 114, 'at a moderate speed'
    ANDANTE_MODERATO = 92, 112, 102, 'between andante and moderato'
    ALLEGRETTO = 112, 120, 116, 'moderately fast'  # changed after the 19th century
    ALLEGRO_MODERATO = 116, 120, 118, 'close to, but not quite allegro'
    ALLEGRO = 120, 156, 138, 'fast, quick, and bright'
    MOLTO_ALLEGRO = 124, 156, 140, 'very fast'
    VIVACE = 156, 176, 166, 'lively and fast'
    VIVACISSIMO = 172, 176, 174, 'very fast and lively'  # same as VIVACISSIAMENTE
    ALLEGRISSIMO = 172, 176, 174, 'very fast'  # same as ALLEGRO_VIVACE
    PRESTO = 168, 200, 184, 'very, very fast'
    PRESTISSIMO = 200, 280, 240, 'extremely fast'  # 200 bpm and over

    # -----------
    # Constructor
    # -----------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[2]  # average tempo
        obj.min_tempo = values[0]
        obj.max_tempo = values[1]
        obj.description = values[3]
        return obj

    # TODO: work on overrides (?)


class Tempo:
    """
    Class to represent information about a tempo
    """
    # -------------------
    # Constructor
    # -------------------
    def __init__(self,
                 tempo: Union[int, float, np.inexact, np.integer],  # TODO: how is tempo classified? bpm?
                 tempo_name: Union[str, 'TempoType'] = '',
                 description: str = ''):
        self.tempo = tempo

        if isinstance(tempo_name, TempoType):
            self.tempo_name = tempo_name.name.title()
            self.description = tempo_name.description.capitalize()
        else:
            self.tempo_name = tempo_name
            self.description = description

    # -------------------
    # Overrides
    # -------------------

    # -------------------
    # Class Methods
    # -------------------
    @classmethod
    def find(cls, value: str) -> 'Tempo':
        pass


class TempoAdjustmentType(Enum):
    # TODO: is this necessary? The point of this enum could be simply to add a description/explanation to the most
    # common types of tempo markings. So if a user wanted to get a small description, this package has them included
    """
    Enum to represent common tempo markings used in music
    """
    A_TEMPO = 'resume previous tempo'
    TEMPO_PRIMO = 'return to base tempo'
    AU_MOUVEMENT = 'play the main tempo'

    A_PIACERE = 'at pleasure'
    ASSAI = 'very much'
    CON_GRAZIA = 'gracefully'
    CON_MOTO = 'with movement'
    LAMENTOSO = 'sadly, plaintively'
    LISTESSO = 'at the same speed'  # spelled L'istesso
    MA_NON_TANTO = 'but not so much'
    MA_NON_TROPPO = 'but not too much'
    MAESTOSO = 'stately'
    MOLTO = 'very'
    MENO = 'less'
    PIU = 'more'
    POCO = 'a little'
    SUBITO = 'suddenly'
    QUICKLY = 'quickly'
    TEMPO_COMODO = 'at a comfortable speed'
    # TEMPO_DI = 'at the speed of a...'
    TEMPO_GIUSTO = 'at the consistent, "right", speed, in strict tempo'
    TEMPO_SEMPLICE = 'simple, regular speed'

    LENT = 'slowly'
    MODERE = 'moderately'
    VIF = 'lively'
    VITE = 'fast'
    RAPIDE = 'rapidly'

    LANGSAM = 'slowly'
    LEBHAFT = 'lively'
    MABIG = 'moderately'  # Mäßig
    RASCH = 'quickly'
    SCHNELL = 'fast'
    BEWEGT = 'animated'


class TempoDescriptorType(Enum):
    """
    Enum to represent common descriptors for tempo markings in music
    """
    NONE = 0, ''
    PIU = 1, 'more'
    POCO = 2, 'a little'
    MENO = 3, 'less'
    MOINS = 4, 'less'
    TRES = 5, 'very'
