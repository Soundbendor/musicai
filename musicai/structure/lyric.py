from enum import Enum


# -----------------
# SyllabicType enum
# -----------------
class SyllabicType(Enum):
    """
    Enum to represent which type of syllable
    """
    NONE = 0
    SINGLE = 1
    BEGIN = 2
    MIDDLE = 3
    END = 4


# -----------
# Lyric class
# -----------
class Lyric:
    """
    Class to represent a lyric
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self,
                 text: str = '',
                 syllabic: SyllabicType = SyllabicType.NONE):

        self.text: str = text
        self.syllabic: SyllabicType = syllabic

        self.number: int = 1
        self.y_offset: int = -80  # fix
        # self.extend: int = 0

        self.extends: bool = False
        self.end_line: bool = False
        self.end_paragraph: bool = False
