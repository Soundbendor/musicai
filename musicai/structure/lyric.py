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
class Lyric():
    """
    Class to represent a lyric
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self, text='', syllabic=SyllabicType.NONE):
        self.text = text
        self.syllabic = syllabic
        self.number = 1
        self.y_offset = -80  # fix
        self.extend = 0
        self.end_line = False
        self.end_paragraph = False

