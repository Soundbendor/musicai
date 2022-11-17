import warnings

import numpy as np
from typing import Union
from enum import Enum
# from datetime import date
from structure.measure import Measure
from structure.note import Note, NoteGroup

# -------------------
# GroupingSymbol Enum
# -------------------
from structure.time import Tempo


class GroupingSymbol(Enum):
    """
    Enum to represent how parts will be connected
    """
    NONE = 0, u''
    BRACE = 1, u'\U0001D114'
    BRACKET = 2, u'\U0001D115'
    LINE = 3, u'\U0001D100\U0001D100\U0001D100'
    SQUARE = 4, u'\U0001D101'

    # -------------
    # Constructor
    # -------------
    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        obj.symbol = values[1]
        return obj

    # -------------
    # Constructor
    # -------------
    def __str__(self):
        return self.symbol


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
        self.measures: list[Measure] = []
        self.id = ''  # string which can be used to differentiate parts
        self.name = 'Default'
        self.auto_update_barline_end = True

        # 2D array of measures for multi-staved parts
        self.multi_staves: list[list[Measure]] = []
        self.grouping_symbol = GroupingSymbol.NONE

        # To-consider: all staves, including the first, could be represented in an encompassing
        # list[list[Measure]] member

    # ----------
    # Properties
    # ----------
    # TODO: Implement self.measures, based off of a total, all-encompassing self.staves of type list[list[Measure]]...
    # @property
    # def measures(self) -> list[Measure] | None:
    #     if len(self.multi_staves) > 0:
    #         return self.multi_staves[0]
    #     else:
    #         return None  # or return [] ?

    # @measures.setter
    # def measures(self, value: list[Measure]):
    #     if len(self.multi_staves) > 0:
    #         self.multi_staves[0] = value
    #     else:
    #         self.multi_staves.append(value)

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''

        # Multi-staff part:
        if len(self.multi_staves) > 0:

            ret_str += '((Multi-staved))\n'

            # FIRST MEASURE
            ret_str += 'Staff 0\n'
            for measure in self.measures:
                if measure is None:
                    raise ValueError('Measure is None')
                ret_str += f'(k={measure.key} c={measure.clef} t={measure.time}) '
                ret_str += str(measure) + ' '
            ret_str += '\n'

            # REMAINING MEASURES
            multi_staff_count = 1
            for measure_list in self.multi_staves:
                ret_str += f'Staff {multi_staff_count}\n'
                for measure in measure_list:
                    if measure is None:
                        raise ValueError('Measure is None')
                    ret_str += f'(k={measure.key} c={measure.clef} t={measure.time}) '
                    ret_str += str(measure) + ' '

        # Single-staff part
        else:
            for measure in self.measures:
                if measure is None:
                    raise ValueError('Measure is None')
                ret_str += str(measure) + ' '

        return ret_str

    # ---------
    # Methods
    # ---------
    def append(self, measure: Measure, staff: int = 1):
        """
        Appends a measure to this part's list of measures. If the staff argument is not 1, the appended measure will
         be added to the corresponding staff. Automatically updates the barline if auto_update_barline_end
         is set to true
        :param measure:
        :param staff:
        :return:
        """
        if staff == 1:
            # Primary staff
            self.measures.append(measure)

        else:

            # Makes sure the secondary staff exists
            while len(self.multi_staves) < (staff - 1):
                self.multi_staves.append([])

            # Append to this secondary-staff
            # -2 because the 2nd staff starts at multi_staves[0]
            self.multi_staves[staff - 2].append(measure)

        if self.auto_update_barline_end:
            self.update_final_barline(staff)

    def update_final_barline(self, staff: int = 1) -> None:
        """
        Used to automatically make the last measure in a part have a final barline, typically called
        when a part has a measure appended. Does not affect non-regular barlines
        """
        from structure.measure import Barline, BarlineLocation, BarlineType

        # UPDATE FIRST STAFF
        if staff == 1:
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

        # UPDATE NON-FIRST STAFF
        else:
            # The multi-stave index is -2 because the 2nd staff starts at 0
            ms_index = staff - 2

            measure_count = len(self.multi_staves[ms_index])

            # Gives the latest measure a final barline and gives the preceding measure a regular barline
            if measure_count > 1:

                # Sets the preceeding from FINAL barline to REGULAR
                if isinstance(self.multi_staves[ms_index][measure_count - 2].barline, Barline):
                    if self.multi_staves[ms_index][measure_count - 2].barline.is_simple_final_barline():
                        self.multi_staves[ms_index][measure_count -
                                                    2].set_barline('REGULAR')
                else:
                    # This is necessary for some reason...
                    self.multi_staves[ms_index][measure_count -
                                                2].set_barline('REGULAR')

                # Sets the following from REGULAR barline to FINAL
                if not self.multi_staves[ms_index][measure_count - 1].has_irregular_rs_barline():
                    self.multi_staves[ms_index][measure_count -
                                                1].set_barline('FINAL')

            # Gives the latest measure a final barline
            elif measure_count == 1:
                if not self.multi_staves[ms_index][0].has_irregular_rs_barline():
                    self.multi_staves[ms_index][0].set_barline('FINAL')

    def get_note_at_location(self,
                             location: Union[int, np.integer, float, np.inexact],
                             measure_index: Union[int, np.integer]) -> Union[Note, None]:
        """
        Returns the note at the specific location if it exists

        :param location: Where in the measure to find the note, in units of note value
        :param measure_index:
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

        :param index: Which index of the note to get in the measure to find the note
        :param measure_index:
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

    def staff_count(self) -> int:
        return 1 + len(self.multi_staves)

    def has_multiple_staves(self) -> bool:
        return self.staff_count() > 1

    def get_staff(self, staff_index: int) -> list[Measure]:
        """
        Depending on the inputted staff, returns what that list of measures should be

        # TODO: To be changed and made to work with the measures property

        :param staff_index: Starting at 0 to represent the primary measure
        :return:
        """

        if staff_index == 0:
            return self.measures

        else:
            assert staff_index - 1 < len(self.multi_staves)
            return self.multi_staves[staff_index - 1]


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
        self.grouping_symbol = GroupingSymbol.NONE

    # --------
    # Override
    # --------
    def __str__(self):
        ret_str = ''

        ret_str += self.grouping_symbol.symbol
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

        # Need to implement a beatmap system which vertically tracks the tempo for all instruments
        # Only supports one tempo currently
        # TODO: Deprecate this
        self.tempo: Tempo | None = None

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

    def __getitem__(self, func):
        if isinstance(func, slice):
            # possibly find recursive solution?
            for system in self.systems:
                for part in system.parts:
                    part.measures = part.measures[func]
                        # TODO: Add floating point functionality for measure and edit measure class

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
            print(f'-------------------------------')
            print(f'System: {system_index}')
            print(
                f'Number of parts in system {system_index}: {len(system.parts)}')

            part_index = 0
            for part in system.parts:

                print(f'----Part {part_index}----')
                print(
                    f'Number of measures in part {part_index}: {len(part.measures)}')
                print(f'{part}')
                # for measure in part.measures:
                #     print(f'(k={measure.key} c={measure.clef} t={measure.time}) {measure} ', end='')
                part_index += 1

            system_index += 1
            print(f'\n-------------------------------\n')

    def append_to_latest_partsystem(self, appended_part: Part) -> None:
        """
        Appends a part to this score's latest partsystem

        :param appended_part:
        :return:
        """
        if len(self.systems) == 0:
            warnings.warn(
                f'There is no partsystem avaiable to append {appended_part} to.', stacklevel=2)
            return

        latest_index = len(self.systems) - 1
        self.systems[latest_index].append(appended_part)

    def get_part_by_mxml_index(self, value: int) -> Part:
        """
        Gets the score's part based on the mxml index, derived from mxml text such as "P1", "P2", "P9", "P12", etc.
        The integer to the right of "P" is what is inserted to to this method

        :param value: An integer greater than 1
        :return:
        """
        current_count = 1
        system_index = 0
        part_index = 0

        # Finds the correct part
        while current_count < value:

            # Increment to the next existing part index
            if part_index < len(self.systems[system_index].parts) - 1:
                part_index += 1

            # No more parts exist in this system; increment the system index and begin at the new part index
            else:
                system_index += 1
                part_index = 0

            current_count += 1

        return self.systems[system_index].parts[part_index]

    def set_part_by_mxml_index(self, new_part: Part, value: int) -> None:
        """
        Sets the score's part based on the mxml index, derived from mxml text such as "P1", "P2", "P9", "P12", etc.
        The integer to the right of "P" is what is inserted to this method

        :param new_part:
        :param value: An integer greater than 1
        :return:
        """
        current_count = 1
        system_index = 0
        part_index = 0

        # Finds the correct part
        while current_count < value:

            # Increment to the next existing part index
            if part_index < len(self.systems[system_index].parts) - 1:
                part_index += 1

            # No more parts exist in this system; increment the system index and begin at the new part index
            else:
                system_index += 1
                part_index = 0

            current_count += 1

        self.systems[system_index].parts[part_index] = new_part

    def add_to_pitch(self, added_num: int = 1) -> None:
        """
        Used for the CUE demo. Goes through every note in the score, and adds "1" to every pitch.

        :return:
        """

        for part_sys in self.systems:
            for part in part_sys.parts:

                # PRIMARY STAFF
                for measure in part.measures:
                    for note in measure.notes:

                        # NOTE GROUPS
                        if isinstance(note, NoteGroup):
                            for grouped_note in note.notes:
                                if grouped_note.is_pitched:
                                    grouped_note.pitch += added_num

                        # NOTES
                        elif isinstance(note, Note):
                            if note.is_pitched:
                                note.pitch += added_num

                # SECONDARY STAFF
                for all_staves in part.multi_staves:
                    for sec_measure in all_staves:
                        for note in sec_measure.notes:

                            # NOTE GROUPS
                            if isinstance(note, NoteGroup):
                                for grouped_note in note.notes:
                                    if grouped_note.is_pitched:
                                        grouped_note.pitch += added_num

                            # NOTES
                            elif isinstance(note, Note):
                                if note.is_pitched:
                                    note.pitch += added_num
