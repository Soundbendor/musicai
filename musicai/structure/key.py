from enum import Enum
import numpy as np
from scipy import stats, linalg

from musicai.structure.pitch import Chromatic, Step, Accidental, Pitch, Octave

# -------------
# ModeType enum
# -------------
class ModeType(Enum):
    """
    ModeType defines the mode of a scale
    """

    MAJOR = 0
    MINOR = 1
    DORIAN = 2
    PHYRGIAN = 3
    LYDIAN = 4
    MIXOLYDIAN = 5
    AEOLIAN = 6
    IONIAN = 7
    LOCRIAN = 8

    # --------
    # Override
    # --------
    def __int__(self):
        return self.value

    def __str__(self):
        return ('{0}'.format(self.name)).title()

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def find(cls, value: str) -> 'ModeType':
        if len(value) == 1:
            if value == 'M':
                return ModeType.MAJOR
            elif value == 'm':
                return ModeType.MINOR
        else:
            for name, member in cls.__members__.items():
                if member.name == value.upper():
                    return ModeType[name]

# ------------
# KeyType enum
# ------------
class KeyType(Enum):
    """
    KeyType defines the mode of a scale
    """

    # (major, minor) where positive => sharps and negative => flats
    Cbb = (-14, -17)  # eqv. to Bb major, Bb minor
    Gbb = (-13, -16)  # eqv. to F major, F minor
    Dbb = (-12, -15)  # eqv. to C major, C minor
    Abb = (-11, -14)  # eqv. to G major, G minor
    Ebb = (-10, -13)  # eqv. to D major, D minor
    Bbb = (-9, -12)  # eqv. to A major, A minor
    Fb = (-8, -11)  # eqv. to E major, E minor
    Cb = (-7, -10)
    Gb = (-6, -9)
    Db = (-5, -8)
    Ab = (-4, -7)
    Eb = (-3, -6)
    Bb = (-2, -5)
    F = (-1, -4)
    C = (0, -3)
    G = (1, -2)
    D = (2, -1)
    A = (3, 0)
    E = (4, 1)
    B = (5, 2)
    Cs = (7, 4)
    Gs = (8, 5)  # eqv. to Ab major, Ab minor
    Ds = (9, 6)  # eqv. to Eb major, Eb minor
    As = (10, 7)  # eqv. to Bb major, Bb minor
    Es = (11, 8)  # eqv. to F major, Es minor
    Bs = (12, 9)  # eqv. to C major, Bs minor
    Fss = (13, 10)  # eqv. to G major, Fss minor
    Css = (14, 11)  # eqv. to D major, Css minor
    NONE = (0, 0)

    # -----------
    # Constructor
    # -----------
    def __init__(self, major_fifths, minor_fifths):
        self.major_fifths = major_fifths
        self.minor_fifths = minor_fifths

    # ----------
    # Properties
    # ----------
    def fifths(self, mode):
        # TODO: handle other modes
        return self.minor_fifths if mode == ModeType.MINOR else self.major_fifths  #WRONG

    # --------
    # Override
    # --------
    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{self.__class__.__name__}({self.name})>'.format(self=self)

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def find(cls, value, mode=ModeType.MAJOR):
        if isinstance(value, KeyType):
            return value
        elif isinstance(value, (float, np.inexact, int, np.integer)):
            idx = 0 if mode == ModeType.MAJOR else 1
            for name, member in cls.__members__.items():
                if member.value[idx] == value:
                    return name
        elif isinstance(value, str):
            if value.title() in cls.__members__:
                return KeyType[value.title()]
            else:
                raise ValueError(f'Unable to match value {value} to KeyType.')
        else:
            raise ValueError(f'Invalid type {type(value)} for KeyType.')

    @classmethod
    def find_pitch_class(cls, pitch_class, mode=ModeType.MAJOR):
        pitch_class = pitch_class % 12

        root_map = [KeyType.C, KeyType.Cs, KeyType.D, KeyType.Eb, KeyType.E, KeyType.F,
                    KeyType.Fs, KeyType.G, KeyType.Ab, KeyType.A, KeyType.Bb, KeyType.B]

        if mode == ModeType.MAJOR:
            return root_map[pitch_class]
        elif mode == ModeType.MINOR:
            return root_map[pitch_class]
        else:
            raise NotImplementedError('Key-finding for the ' + str(mode) + ' mode is not supported.')


# ------------
# Scale class
# ------------
class Scale:
    """
     Class to represent a musical scale
     """
    __scales = {
        KeyType.Cbb: [
            # Cbb Major (theoretical)
            [
                # TODO
            ],
            # Cbb Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
        KeyType.Gbb: [
            # Gbb Major (theoretical)
            [
                # TODO
            ],
            # Gbb Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
        KeyType.Dbb: [
            # Dbb Major (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, None, Chromatic.Fb, Chromatic.Gbb,
                None, Chromatic.Abb, None, Chromatic.Bb, None, Chromatic.Cb
            ],
            # Dbb Natural Minor (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, Chromatic.Fbb, None, Chromatic.Gbb,
                None, Chromatic.Abb, Chromatic.Bbbb, None, Chromatic.Cbb, None
            ]
        ],
        KeyType.Abb: [
            # Abb Major (theoretical)
            [
                Chromatic.Dbb, None,Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, Chromatic.Abb, None, Chromatic.Bb, None, Chromatic.Cb
            ],
            # Abb Natural Minor (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, Chromatic.Fbb, None, Chromatic.Gbb,
                None, Chromatic.Abb, None, Chromatic.Bbb, Chromatic.Cbb, None
            ]
        ],
        KeyType.Ebb: [
            # Ebb Major (theoretical)
            [
                None, Chromatic.Db, Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, Chromatic.Abb, None, Chromatic.Bb, None, Chromatic.Cb
            ],
            # Ebb Natural Minor (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, None, Chromatic.Fb, Chromatic.Gbb,
                None, Chromatic.Abb, None, Chromatic.Bbb, Chromatic.Cbb, None
            ]
        ],
        KeyType.Bbb: [
            # Bbb Major
            [
                None, Chromatic.Db, Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, Chromatic.Bbb, None, Chromatic.Cb
            ],
            # Bbb Natural Minor (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, None, Chromatic.Fb, Chromatic.Gbb,
                None, Chromatic.Abb, None, Chromatic.Bbb, None, Chromatic.Cb
            ]
        ],
        KeyType.Fb: [
            # Fb Major (theoretical)
            [
                None, Chromatic.Db, None, Chromatic.Eb, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, Chromatic.Bbb, None, Chromatic.Cb
            ],
            # Fb Natural Minor (theoretical)
            [
                Chromatic.Dbb, None, Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, Chromatic.Abb, None, Chromatic.Bbb, None, Chromatic.Cb
            ]
        ],

        KeyType.Cb: [
            # Cb Major
            [
                None, Chromatic.Db, None, Chromatic.Eb, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, Chromatic.Cb
            ],
            # Cb Natural Minor (theoretical)
            [
                None, Chromatic.Db, Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, Chromatic.Abb, None, Chromatic.Bbb, None, Chromatic.Cb
            ]
        ],
        KeyType.Gb: [
            # Gb Major
            [
                None, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, Chromatic.Cb
            ],
            # Gb Natural Minor (theoretical)
            [
                None, Chromatic.Db, Chromatic.Ebb, None, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, Chromatic.Bbb, None, Chromatic.Cb
            ]
        ],
        KeyType.Db: [
            # Db Major
            [
                Chromatic.C, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, None
            ],
            # Db Natural Minor (theoretical)
            [
                None, Chromatic.Db, None, Chromatic.Eb, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, Chromatic.Bbb, None, Chromatic.Cb
            ]
        ],
        KeyType.Ab: [
            # Ab Major
            [
                Chromatic.C, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, Chromatic.Ab, None, Chromatic.Bb, None
            ],
            # Ab Natural Minor
            [
                None, Chromatic.Db, None, Chromatic.Eb, Chromatic.Fb, None,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, Chromatic.Cb

            ]
        ],
        KeyType.Eb: [
            # Eb Major
            [
                Chromatic.C, None, Chromatic.D, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, Chromatic.Ab, None, Chromatic.Bb, None
            ],
            # Eb Natural Minor
            [
                None, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, Chromatic.Cb
            ]
        ],
        KeyType.Bb: [
            # Bb Major
            [
                Chromatic.C, None, Chromatic.D, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, None, Chromatic.A, Chromatic.Bb, None
            ],
            # Bb Natural Minor
            [
                Chromatic.C, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                Chromatic.Gb, None, Chromatic.Ab, None, Chromatic.Bb, None
            ]
        ],
        KeyType.F: [
            # F Major
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, Chromatic.F,
                None, Chromatic.G, None, Chromatic.A, Chromatic.Bb, None
            ],
            # F Natural Minor
            [
                Chromatic.C, Chromatic.Db, None, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, Chromatic.Ab, None, Chromatic.Bb, None
            ]
        ],
        KeyType.C: [
            # C Major
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, Chromatic.F,
                None, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ],
            # C Natural Minor
            [
                Chromatic.C, None, Chromatic.D, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, Chromatic.Ab, None, Chromatic.Bb, None
            ]
        ],
        KeyType.G: [
            # G Major
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, None,
                Chromatic.Fs, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ],
            # G Natural Minor
            [
                Chromatic.C, None, Chromatic.D, Chromatic.Eb, None, Chromatic.F,
                None, Chromatic.G, None, Chromatic.A, Chromatic.Bb, None
            ]
        ],
        KeyType.D: [
            # D Major
            [
                None, Chromatic.Cs, Chromatic.D, None, Chromatic.E, None,
                Chromatic.Fs, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ],
            # D Natural Minor
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, Chromatic.F, None, Chromatic.G, None, Chromatic.A,
                Chromatic.Bb, None
            ]
        ],
        KeyType.A: [
            # A Major
            [
                None, Chromatic.Cs, Chromatic.D, None, Chromatic.E, None,
                Chromatic.Fs, None, Chromatic.Gs, Chromatic.A, None, Chromatic.B
            ],
            # A Natural Minor
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, Chromatic.F,
                None, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ]
        ],
        KeyType.E: [
            # E Major
            [
                None, Chromatic.Cs, None, Chromatic.Ds, Chromatic.E, None,
                Chromatic.Fs, None, Chromatic.Gs, Chromatic.A, None, Chromatic.B
            ],
            # E Natural Minor
            [
                Chromatic.C, None, Chromatic.D, None, Chromatic.E, None,
                Chromatic.Fs, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ]
        ],
        KeyType.B: [
            # B Major
            [
                None, Chromatic.Cs, None, Chromatic.Ds, Chromatic.E, None,
                Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, Chromatic.B
            ],
            # B Natural Minor
            [
                None, Chromatic.Cs, Chromatic.D, None, Chromatic.E, None,
                Chromatic.Fs, Chromatic.G, None, Chromatic.A, None, Chromatic.B
            ]
        ],
        #KeyType.Fs: [
        #     # Fs Major
        #     [
        #         None, Chromatic.Cs, None, Chromatic.Ds, None, Chromatic.Es,
        #         Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, Chromatic.B
        #     ],
        #     # Fs Natural Minor
        #     [
        #         None, Chromatic.Cs, Chromatic.D, None, Chromatic.E, None, Chromatic.Fs, None, Chromatic.Gs,
        #         Chromatic.A, None, Chromatic.B
        #     ]
        #],
        KeyType.Cs: [
            # Cs Major
            [
                Chromatic.Bs, Chromatic.Cs, None, Chromatic.Ds, None, Chromatic.Es,
                Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, None
            ],
            # Cs Natural Minor
            [
                None, Chromatic.Cs, None, Chromatic.Ds, Chromatic.E, None,
                Chromatic.Fs, None, Chromatic.Gs, Chromatic.A, None, Chromatic.B
            ]
        ],
        KeyType.Gs: [
            # Gs Major (theoretical)
            [
                Chromatic.Bs, Chromatic.Cs, None, Chromatic.Ds, None, Chromatic.Es,
                None, Chromatic.Fss, Chromatic.Gs, None, Chromatic.As, None
            ],
            # Gs Natural Minor
            [
                None, Chromatic.Cs, None, Chromatic.Ds, Chromatic.E, None,
                Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, Chromatic.B
            ]
        ],
        KeyType.Ds: [
            # Ds Major (theoretical)
            [
                Chromatic.Bs, None, Chromatic.Css, Chromatic.Ds, None, Chromatic.Es,
                None, Chromatic.Fss, Chromatic.Gs, None, Chromatic.As, None
            ],
            # Ds Minor
            [
                None, Chromatic.Cs, None, Chromatic.Ds, None, Chromatic.Es,
                Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, Chromatic.B
            ]
        ],
        KeyType.As: [
            # As Major (theoretical)
            [
                Chromatic.Bs, None, Chromatic.Css, Chromatic.Ds, None, Chromatic.Es,
                None, Chromatic.Fss, None, Chromatic.Gss, Chromatic.As, None
            ],
            # As Natural Minor
            [
                Chromatic.Bs, Chromatic.Cs, None, Chromatic.Ds, None, Chromatic.Es,
                Chromatic.Fs, None, Chromatic.Gs, None, Chromatic.As, None
            ]
        ],
        KeyType.Es: [
            # Es Major (theoretical)
            [
                # TODO
            ],
            # Es Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
        KeyType.Bs: [
            # Bs Major (theoretical)
            [
                # TODO
            ],
            # Bs Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
        KeyType.Fss: [
            # Fss Major (theoretical)
            [
                # TODO
            ],
            # Fss Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
        KeyType.Css: [
            # Css Major (theoretical)
            [
                # TODO
            ],
            # Css Natural Minor (theoretical)
            [
                # TODO
            ]
        ],
    }

    # -----------
    # Constructor
    # -----------
    def __init__(self, key):
        self.key = key

    # ---------
    # Methods
    # ---------
    def find(self, midi):
        pitch_class = midi % 12
        return Scale.__scales[self.key.keytype][int(self.key.modetype)][pitch_class]

    # -------------
    # Class Methods
    # -------------


# ---------
# Key class
# ---------
class Key:
    """
    Class to represent a musical key
    """
    SHARPS = [Step.F, Step.C, Step.G, Step.D, Step.A, Step.E, Step.B]
    FLATS = [Step.B, Step.E, Step.A, Step.D, Step.G, Step.C, Step.F]

    # -----------
    # Constructor
    # -----------
    def __init__(self, keytype=KeyType.C, modetype=ModeType.MAJOR):
        self.keytype = KeyType.find(keytype)
        self.modetype = modetype
        self.scale = Scale(self)

    # ----------
    # Properties
    # ----------
    @property
    def glyph(self):
        if self.is_flat():
            return 'accidentalFlat'
        elif self.is_sharp():
            return 'accidentalSharp'
        return ''

    # --------
    # Override
    # --------
    def __str__(self) -> str:
        return str(self.keytype) + ' ' + str(self.modetype)

    # ---------
    # Methods
    # ---------
    def degree(self, midi: int) -> Chromatic:
        return self.scale.find(midi)

    def has_accidental(self, midi: int) -> bool:
        return self.degree(midi) is None

    def is_flat(self):
        return self.keytype.fifths(self.modetype) < 0

    def is_sharp(self):
        return self.keytype.fifths(self.modetype) > 0

    def is_neutral(self):
        return self.keytype.fifths(self.modetype) == 0

    def fifths(self):
        return self.keytype.fifths(self.modetype)

    def altered(self):
        if self.is_flat():
            return Key.FLATS[0:abs(self.fifths())]
        elif self.is_sharp():
            return Key.SHARPS[0:abs(self.fifths())]
        else:
            # CMaj or Amin
            return []

    def find_pitch(self, midi):
        pitch_class = midi % 12
        pitch_height = midi // 12
        step = self.scale.find(pitch_class)

        if step is not None:
            pitch = Pitch((step, Octave.find(pitch_height)), alter=Accidental.NONE)
        else:
            if Step.has_value(pitch_class):
                # add natural sign
                step = Step(pitch_class)
                accidental = Accidental.NATURAL
                pitch = Pitch((step, Octave.find(pitch_height)), alter=Accidental.NATURAL)
            else:
                alter = 0
                accidental = Accidental.NONE
                if self.keytype.fifths(self.modetype) >= 0:
                    # add sharp
                    alter = -1
                    accidental = Accidental.SHARP
                else:
                    # add flat
                    alter = 1
                    accidental = Accidental.FLAT
                step = Step(pitch_class + alter)
                if step is not None:
                    suffix = 'b' if alter >= 0 else 's'
                    chromatic = Chromatic[str(step) + suffix]
                    pitch = chromatic.pitch
                    return pitch
                else:
                    raise ValueError('Error: could not match midi note {0} in key {1}'.format(midi, self))
        return pitch

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def find(cls, key) -> 'Key':
        pass


    @classmethod
    def find_key(cls, pitch_histogram):
        """ Krumhansl-Schmuckler key-finding algorithm

            Source: https://gist.github.com/bmcfee/1f66825cef2eb34c839b42dddbad49fd
        """
        X = stats.zscore(pitch_histogram)

        # Coefficients from Kumhansl and Schmuckler
        # as reported here: http://rnhart.net/articles/key-finding/
        major = np.asarray([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        major = stats.zscore(major)

        minor = np.asarray([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        minor = stats.zscore(minor)

        major = linalg.circulant(major)
        minor = linalg.circulant(minor)

        major_r = major.T.dot(X)
        minor_r = minor.T.dot(X)

        mode = ModeType.MAJOR
        if np.max(major_r) > np.max(minor_r):
            mode = ModeType.MAJOR
            root = np.argmax(major_r)
        else:
            mode = ModeType.MINOR
            root = np.argmax(minor_r)

        major_fifths = [0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5]
        minor_fifths = [-3, 4, 1, -6, -1, -4, 3, -2, 5, 0, -5, 2]

        if mode is ModeType.MAJOR:
            return Key(KeyType.find(major_fifths[root], mode), mode)
        else:
            return Key(KeyType.find(minor_fifths[root], mode), mode)