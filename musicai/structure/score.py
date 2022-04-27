import numpy as np
from typing import Union
from datetime import date
from musicai.structure.measure import Measure
from musicai.structure.note import Note


# ----------
# Part class
# ----------
class Part:
    """
    Class to represent a Part
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        from musicai.structure.measure import BarlineType
        self.measures: list[Measure] = []
        self.id = ''  # string which can be used to differentiate parts
        self.name = 'Default'
        self.auto_update_barline_end = True


    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for measure in self.measures:
            if measure is None:
                raise ValueError('Measure is None')
            ret_str += str(measure) + ' '

        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, measure):
        self.measures.append(measure)

        if self.auto_update_barline_end:
            self.update_final_barline()

    def update_final_barline(self) -> None:
        """
        Used to automatically make the last measure in a part have a final barline, typically called
        when a part has a measure appended. Does not affect non-regular barlines

        """
        from musicai.structure.measure import Barline, BarlineLocation, BarlineType
        measure_count = len(self.measures)

        # Gives the latest measure a final barline and gives the preceding measure a regular barline
        if measure_count > 1:

            # Sets the preceeding from FINAL barline to REGULAR
            if isinstance(self.measures[measure_count - 2].barline, Barline):
                if self.measures[measure_count - 2].barline.is_simple_final_barline():
                    self.measures[measure_count - 2].set_barline('REGULAR')
            else:
                # This is necessary for some reason...
                self.measures[measure_count - 2].set_barline('REGULAR')

            # Sets the following from REGULAR barline to FINAL
            if not self.measures[measure_count - 1].has_irregular_rs_barline():
                self.measures[measure_count - 1].set_barline('FINAL')

        # Gives the latest measure a final barline
        elif measure_count == 1:
            if not self.measures[0].has_irregular_rs_barline():
                self.measures[0].set_barline('FINAL')

    def get_note_at_location(self,
                             location: Union[int, np.integer, float, np.inexact],
                             measure_index: Union[int, np.integer]) -> Union[Note, None]:
        """
        Returns the note at the specific location if it exists

        :param location: Where in the measure to find the note, in units of note value
        :return: The note is returned if one exists at or after the location; otherwise, None is returned
        """

        current_location = 0
        return_note = None

        # Loop through every note until we hit the destination
        for n in self.measures[measure_index].notes:

            # If this is the first note equal to or after the desired location, then return it
            if location <= current_location:
                return_note = n
                break

            # Otherwise, we have not hit the right now yet
            current_location += n.value

        # Check for Measure Marks in this measure
        # If there is an Octave Line over the note, this will be reflected
        if return_note is not None:
            pass

        # Note: duration == (NoteType * divisions * 4) * dots * self.ratio.normal / self.ratio.actual
        return return_note

    def get_note_at_index(self,
                             index: Union[int, np.integer],
                             measure_index: Union[int, np.integer]) -> Union[Note, None]:
        """
        Returns the note at the specific index if it exists

        :param location: Which index of the note to get in the measure to find the note
        :return: The note is returned if one exists at or after the location; otherwise, None is returned
        """

        return_note = None

        if index < len(self.measures[measure_index].notes):
            return_note = self.measures[measure_index].notes[index]

        # Check for Measure Marks in this measure
        # If there is an Octave Line over the note, this will be reflected
        if return_note is not None:
            pass

        # Note: duration == (NoteType * divisions * 4) * dots * self.ratio.normal / self.ratio.actual
        return return_note


# ----------------
# PartSystem class
# ----------------
class PartSystem:
    """
    Class to represent a Part System
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.parts: list[Part] = []

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for part in self.parts:
            if part is None:
                #  ValueError('Part is None')
                pass
            ret_str += str(part) + '\n'
        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, part):
        self.parts.append(part)


# ----------
# Work class
# ----------
class Work:
    """
    Class to represent a Work
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.title = ''
        self.number = 0
        self.composer = ''


# -----------
# Encoding class
# -----------
# class Encoding:
#     """
#     Class to represent information about poeple who did digital encording
#     """
#     def __init__(self):
#         self.name = ''
#         self.date = None  # must be derivated in musicxml...
#         self.software = ''
#         self.description = ''
#         self.support = None  # needs more attributes


# -----------
# Metadata class
# -----------
class Metadata:
    """
    Class to represent information about a score
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.title = ''
        self.number = ''
        self.composer = ''
        self.creators = []  # list of creator tuples (title, name)
        self.rights = []  # list of right tuples (description, type)
        # self.encording = []
        self.source = ''

        self.work_title = ''
        self.work_number = None
        self.opus_link = ''

    # -----------
    # Methods
    # -----------
    def append_right(self, description: str, rights_type: str = ''):
        self.rights.append((description, rights_type))


# -----------
# Score class
# -----------
class Score:
    """
    Class to represent a Score
    """
    # -----------
    # Constructor
    # -----------
    def __init__(self):
        self.filename = ''
        self.systems: list[PartSystem] = []
        self.metadata = Metadata()

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''
        for system in self.systems:
            if system is None:
                raise ValueError('system is None')
            ret_str += str(system) + ' '

        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, system):
        self.systems.append(system)

    def print_measure_marks(self):
        """
        Loops through every measure in each part and prints a measure there if one exists

        :return:
        """
        print('=====Measure Marks:=====')
        for part_sys in self.systems:
            part_index = 0

            for parts in part_sys.parts:

                print(f'===Part {part_index}===')
                for measure_index in range(len(parts.measures)):

                    # If there are measure marks in this measure, then output it
                    if len(parts.measures[measure_index].measure_marks) != 0:
                        print(f'Measure {measure_index}: '
                              f'{[repr(mm) for mm in parts.measures[measure_index].measure_marks]}')
                part_index += 1

        print('\n')

    def print_in_depth(self):
        print(f'\n')
        print(f'Score:')
        print(f'======================')
        print(f'Number of systems: {len(self.systems)}')
        print(f'======================')

        system_index = 0
        for system in self.systems:
            print(f'--------------------')
            print(f'System: {system_index}')
            print(f'Number of parts in system {system_index}: {len(system.parts)}')

            part_index = 0
            for part in system.parts:

                print(f'Part {part_index}--------')
                print(f'Number of measures in part {part_index}: {len(part.measures)}')
                for measure in part.measures:
                    print(f'(k={measure.key} c={measure.clef} t={measure.time}) {measure} ', end='')
                part_index += 1

            system_index += 1
            print(f'\n--------------------\n')

def get_test_score():
    from musicai.structure.note import Note, NoteType
    from musicai.structure.pitch import Pitch, Step
    from musicai.structure.measure import Measure
    from musicai.structure.score import Part, PartSystem
    from musicai.structure.clef import Clef
    from musicai.structure.key import Key, KeyType, ModeType

    n1 = Note(value=NoteType.EIGHTH, pitch=Pitch('A3'))
    n2 = Note(value=NoteType.EIGHTH, pitch=Pitch('B3'))
    n3 = Note(value=NoteType.EIGHTH, pitch=Pitch('C4'))
    n4 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('D4'))
    n5 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('E4'))
    n6 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('G5'))
    n7 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('A5'))
    n8 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('B5'))
    n9 = Note(value=NoteType.SIXTEENTH, pitch=Pitch('C6'))

    m1 = Measure()

    m1.clef = Clef()  # treble
    #m1.clef = Clef(ClefType.BASS)
    #m1.key = Key()     # CMaj

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