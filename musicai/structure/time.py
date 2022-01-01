from enum import Enum

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

    # --------
    # Override
    # --------
    def __str__(self):
        return ('{0}'.format(self.name)).lower()

    def __repr__(self):
        return '{0}({1})'.format(self.name, self.value)

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
        return '<TimeSignature: ' + str(self.numerator) + '/' + str(self.denominator) + '; ' + self.timesymboltype.__repr__() + '>'

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
            raise ValueError('Cannot find TimeSignature for {0}.'.format(time))
