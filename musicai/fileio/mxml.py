import warnings
import xml.etree.ElementTree as ET

import numpy as np
from typing import Union

from musicai.structure.note_mark import StemType, Beam, BeamType, TieType
from musicai.structure.clef import Clef, ClefOctave
from musicai.structure.key import ModeType, KeyType, Key
from musicai.structure.lyric import Lyric, SyllabicType
from musicai.structure.measure import Measure
from musicai.structure import measure_mark
from musicai.structure.measure_mark import MeasureMark, InstantaneousMeasureMark
from musicai.structure.note import NoteType, Ratio, NoteValue, Rest, Note
from musicai.structure.pitch import Accidental, Pitch, Octave, Step
from musicai.structure.score import Score, PartSystem, Part
from musicai.structure.time import TimeSignature


class MeasureMarkFromXML:
    from musicai.structure.measure_mark import HairpinType

    # -----------
    # Class Methods
    # -----------
    @classmethod
    def hairpin_type(cls, value: Union[str, int, np.integer]) -> 'HairpinType':
        from musicai.structure.measure_mark import HairpinType
        if isinstance(value, str):
            if not value.isnumeric():
                warnings.warn(f'Cannot make a HairpinType from xml attribute of string {value}. Defaulting to '
                              f'HairpinType.STANDARD', stacklevel=2)
                return HairpinType.STANDARD
            else:
                xml_numeric = int(value)

        elif isinstance(value, Union[int, np.integer]):
            xml_numeric = value

        else:
            warnings.warn(f'Cannot make a HairpinType from xml attribute of type {type(value)}. Defaulting to '
                          f'HairpinType.STANDARD', stacklevel=2)
            return HairpinType.STANDARD

        if xml_numeric in [ht.value for ht in HairpinType]:
            return HairpinType(xml_numeric)

        else:
            warnings.warn(f'Cannot make a HairpinType from xml attribute of value {xml_numeric}. Defaulting to '
                          f'HairpinType.STANDARD', stacklevel=2)
            return HairpinType.STANDARD


class MusicXML:
    # -----------
    # Class Methods
    # -----------
    @staticmethod
    def load(xml_file: str) -> Score:
        """
        Loads a MusicXML file and converts to a Score.


        """

        def _load_partwise(loaded_root: ET.Element) -> Score:
            new_score = Score()
            new_system = PartSystem()

            for partwise_item in loaded_root:
                match partwise_item.tag:
                    case 'movement-title':  # title of movement
                        new_score.metadata.title = partwise_item.text

                    case 'movement-number':  # number of movement
                        new_score.metadata.number = partwise_item.text

                    case 'identification':  # metadata of the score
                        for ident_element in partwise_item:
                            match ident_element.tag:
                                case 'creator':  # creators of the score
                                    if 'type' in ident_element.attrib.keys():  # if the dictionary properly exists

                                        # IF the main composer hasn't been set yet--this is checked for first
                                        if ident_element.get('type').lower() == 'composer' \
                                                and new_score.metadata.composer == '':
                                            new_score.metadata.composer = ident_element.text
                                            # TODO: If there's no 'composer' type, then the main composer is never set
                                        else:
                                            creator_tuple = (ident_element.get('type'), ident_element.text)
                                            new_score.metadata.creators.append(creator_tuple)

                                    else:  # the dictionary doesn't properly exist
                                        creator_tuple = ('Creator', ident_element.text)
                                        new_score.metadata.creators.append(creator_tuple)

                                case 'rights':
                                    if 'type' in ident_element.attrib.keys():  # if the type is defined
                                        new_score.metadata.append_right(ident_element.text, ident_element.get('type'))
                                    else:
                                        new_score.metadata.append_right(ident_element.text, '')

                                case 'encoding':  # people who did digital encoding for the file
                                    print('Encoding registered, ', ident_element.text)  # TODO

                                case 'source':  # source of the encoded music
                                    new_score.metadata.source = ident_element.text

                                case 'relation':  # related resource to the encoded music
                                    print('relation registered, ', ident_element.text)  # TODO

                                case 'miscellaneous':  # custom metadata
                                    print('Misc info registered, ', ident_element.text)  # TODO

                                case _:
                                    NotImplementedError(f'Unknown element \"{ident_element.tag}\" under the '
                                                        f'identification element.')

                    case 'work':  # basic information of the work
                        for work_element in partwise_item:
                            match work_element.tag:
                                case 'work-number':
                                    new_score.metadata.work_number = work_element.text
                                case 'work-title':
                                    new_score.metadata.work_title = work_element.text
                                case 'opus':
                                    print('opus registered, ', work_element.text)  # TODO
                                case _: warnings.warn(f'Unknown element \"{work_element.tag}\" under the work '
                                                      f'element.', stacklevel=2)

                    case 'defaults':  # score-wide scaling defaults
                        print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')  # TODO

                    case 'credit':  # appearence of information on the front pages
                        print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')  # TODO

                    case 'part-list':  # titles and info about parts of the document
                        print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')  # TODO
                        # TODO: Make this go AFTER <parts>?

                    case 'part':  # parts which contain measures
                        print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')
                        part = _load_part(partwise_item)
                        new_system.append(part)

                    case _:
                        raise NotImplementedError(f'Unknown element \"{partwise_item.tag}\" in musicxml file.')

            new_score.append(new_system)
            return new_score

        def _load_part(part_item: ET.Element) -> Part:
            time = None
            key = None
            divisions = None

            part = Part()
            measure_marks: list[MeasureMark] = []

            if 'id' in part_item.attrib.keys():
                part.id = part_item.get('id')
            else:
                warnings.warn(f'Part has no ID in musicxml file', stacklevel=2)
            # TODO: Need to find a way to pull info from the part in <part-list>

            # Establishes the initial divisions value
            if part_item.find('measure').find('attributes').find('divisions') is not None:
                divisions = int(part_item.find('measure').find('attributes').find('divisions').text)
            else:
                raise ImportError('No initial divisions value found')

            for item in part_item:
                # print('Part from _load_part(): ', part)  # TODO: When this is uncommented, it ruins things?
                if item.tag == 'measure':
                    loaded_measure = _load_measure(item, Measure(time=time, key=key), divisions, len(part.measures),
                                                   measure_marks)

                    measure_marks = loaded_measure[1]
                    part.append(loaded_measure[0])

                    # Updates the divisions amount if applicable
                    for attribute_element in item.findall('attributes'):
                        if attribute_element.find('divisions') is not None:
                            divisions = int(attribute_element.find('divisions').text)
                else:
                    raise NotImplementedError(f'The non-measure element "{item.tag}" is under the Parts element')

                # update time and key signatures, to be used future measures
                if loaded_measure[0].time is not None:
                    time = loaded_measure[0].time
                else:
                    loaded_measure[0].time = time

                if loaded_measure[0].key is not None:
                    key = loaded_measure[0].key
                else:
                    loaded_measure[0].key = key

                # Implement every completed measure mark:
                for mm in measure_marks:
                    # A non-InstantaneousMeasureMark is completed if it's end_point is not 0
                    if mm is not InstantaneousMeasureMark and mm.end_point != 0:

                        if mm.measure_index < len(part.measures):
                            print(
                                f'MM starting at {mm.start_point}, ending at '
                                f'{mm.end_point}, with measure_span {mm.measure_span} has been added to measure '
                                f'{mm.measure_index}!')

                            # Append the MeasureMark to the part's measure
                            part.measures[mm.measure_index].measure_marks.append(mm)
                            # Remove this MeasureMark from the running-total list of measure marks
                            measure_marks.remove(mm)

                # MeasureMarks that have not been resolved yet are noted to span for +1 measure
                for mm in measure_marks:
                    if isinstance(mm, MeasureMark):
                        print(f'incrementing measure span for {mm}')
                        mm.measure_span += 1

                print(f'\nCurrent persisting MeasureMarks: {measure_marks}\n')



            # At the end of the constructed part:
            # Unresolved MeasureMarks are now wrapped up, with their end being at the score-end
            for mm in measure_marks:
                mm.end_point = 0
                part.measures[mm.measure_index].measure_marks.append(mm)

            return part

        def _load_measure(measure_element: ET.Element,
                          measure: Measure,
                          divisions: int,
                          measure_index: int,
                          measure_marks: list[MeasureMark]) -> (Measure, list[MeasureMark]):
            """
            Loads a measure element from a partwise musicxml file

            :param measure_element: The musicxml measure element to be loaded
            :param measure: The measure which describes what key and clef the measure will take place in
            :param divisions: Divisions per quarter note, used to compute the note's value
            :param measure_index: Dictates what index this measure will be in the part list it's appended to
            :param measure_marks: List used to keep a running total of to-be-inserted measure marks
            :return: The measure described by the xml file and an updated list of MeasureMarks
            """
            print('=====measure=====')

            current_musical_location = 0  # incremented as more notes are added

            n = 1
            for item in measure_element:

                print(f'{n}: Reading item of tag {item.tag} at location {current_musical_location}')
                n += 1

                match item.tag:

                    case 'attributes':
                        for child in item:
                            match child.tag:
                                case 'clef':
                                    measure.display_clef = True
                                    clef_octave = 0
                                    clef_line = 3
                                    clef_number = 0
                                    clef_sign = 'G'

                                    if 'number' in child.attrib.keys():
                                        clef_number = child.get('number')
                                    # TODO: Implement other clef elements
                                    for clef_item in child:
                                        if clef_item.tag == 'sign':
                                            clef_sign = clef_item.text
                                        elif clef_item.tag == 'line':
                                            clef_line = int(clef_item.text)
                                        elif clef_item.tag == 'clef-octave-change':
                                            clef_octave = int(clef_item.text)
                                        else:
                                            warnings.warn(f'Clef element {clef_item.tag.title()} not implemented.')

                                    measure.clef = Clef(clef_sign, clef_octave, clef_line)

                                case 'divisions':
                                    divisions = int(child.text)

                                case 'key':
                                    measure.display_key = True
                                    new_key = Key()

                                    for key_item in child:
                                        if key_item.tag == 'fifths':
                                            new_key.keytype = KeyType.find(int(key_item.text))
                                        elif key_item.tag == 'mode':
                                            new_key.modetype = ModeType[key_item.text.upper()]
                                        else:
                                            raise NotImplementedError(f'key for {key_item.tag}')

                                    measure.key = new_key

                                case 'staves':
                                    print('Multi-staves not supported yet')

                                case 'time':
                                    measure.display_time = True
                                    new_time_signature = TimeSignature()

                                    for time_item in child:
                                        if time_item.tag == 'beats':
                                            new_time_signature.numerator = int(time_item.text)
                                        elif time_item.tag == 'beat-type':
                                            new_time_signature.denominator = int(time_item.text)
                                        else:
                                            print(f'{time_item.tag} is not supported yet')

                                    measure.time = new_time_signature

                                case 'transpose':
                                    print(f'Transposing not supported yet')

                                case 'measure_style':
                                    print(f'Measure Style not supported yet')

                                case _:
                                    print(f'{child.tag.title()} under "Measure" is not supported yet')

                    case 'note':
                        if measure.time is None or measure.key is None:
                            raise ValueError(f'Time and key SHOULD already be set. Set it up to do it manually')

                        loaded_note = _load_note(item, divisions)
                        measure.append(loaded_note[0])
                        current_musical_location += loaded_note[1]

                    case 'backup':
                        pass
                        # print(f'{item.tag.title()} in Measure has not been implemented yet')

                    case 'forward':
                        pass

                    case 'direction':
                        for dir_child in item:
                            if dir_child.tag == 'direction-type':
                                for dir_type in dir_child:
                                    match dir_type.tag:

                                        case 'wedge':
                                            from musicai.structure.measure_mark import DynamicChangeMark

                                            wedge_type = dir_type.get('type').lower()
                                            print('Wedge type acquired: ', wedge_type)

                                            # Wedge creation starts
                                            if wedge_type == 'crescendo' or wedge_type == 'decrescendo':
                                                dcm = DynamicChangeMark(current_musical_location, 0, wedge_type,
                                                                        hairpin=True, divisions=divisions)
                                                # ===== for multi-spanning measures =====
                                                dcm.measure_index = measure_index
                                                dcm.number = dir_type.get('number')
                                                # ========
                                                measure_marks.append(dcm)

                                            # Wedge creation is finished
                                            elif wedge_type == 'stop':

                                                # If this is a numbered wedge mark
                                                if dir_type.get('number') is not None:

                                                    # loops until it finds the corresponding measure mark
                                                    for mm in measure_marks:
                                                        if mm.number == dir_type.get('number') and \
                                                                isinstance(mm, DynamicChangeMark):

                                                            mm.end_point = current_musical_location

                                                            # If this is across a single measure, append it to this
                                                            # measure
                                                            if mm.measure_span == 0:
                                                                print(f'Read wedge with st:{mm.start_point}, end:'
                                                                      f'{mm.end_point}, and measure_span:'
                                                                      f'{mm.measure_span}')

                                                                # Adds the mark to the measure
                                                                measure.measure_marks.append(mm)

                                                                # Removes it from the list
                                                                measure_marks.remove(mm)

                                                            else:
                                                                print(f'Read wedge with st:{mm.start_point}, end:'
                                                                      f'{mm.end_point}, and measure_span:'
                                                                      f'{mm.measure_span}')
                                                                # The MeasureMark will be added outside this method,
                                                                # In the _load_part() method
                                                                pass

                                                            break  # (No way for checking if the loop failed yet)

                                                # Else this is not a numbered wedge mark
                                                # There is likely only one dynamic mark in the list of marks
                                                else:
                                                    for mm in measure_marks:
                                                        if isinstance(mm, DynamicChangeMark):

                                                            mm.end_point = current_musical_location

                                                            if mm.measure_span == 0:
                                                                # The marking is taken out of list to be added to this
                                                                # measure
                                                                print(f'Read wedge with st:{mm.start_point}, end:'
                                                                      f'{mm.end_point}, and measure_span:'
                                                                      f'{mm.measure_span}')
                                                                measure.measure_marks.append(mm)
                                                                measure_marks.remove(mm)

                                                            else:
                                                                print(f'Read wedge with st:{mm.start_point}, end:'
                                                                      f'{mm.end_point}, and measure_span:'
                                                                      f'{mm.measure_span}')
                                                                # The marking will be taken out in the _load_part()
                                                                # function, so that it may be appended to a previous
                                                                # measure
                                                                pass

                                            elif wedge_type == 'continue':
                                                # Not sure if this attribute means anything for this project
                                                pass
                                            else:
                                                warnings.warn(f'Measure mark wedge of value {wedge_type} is not '
                                                              f'supported.', stacklevel=2)

                                        case '':
                                            pass
                                        case _:
                                            pass
                                            # print(f'{dir_type.tag.title()} in Measure has not been implemented yet')

                            elif dir_child.tag == 'staff':
                                pass
                                # print(f'{dir_child.tag.title()} in Measure has not been implemented yet')
                            else:
                                pass
                                # print(f'{dir_child.tag.title()} in Measure has not been implemented yet')

                    case 'harmony':
                        pass
                    case 'figured-bass':
                        pass
                    case 'print':
                        pass
                    case 'sound':
                        pass
                    case 'listening':
                        pass
                    case 'barline':
                        pass
                    case 'grouping':
                        pass
                    case 'link':
                        pass
                    case 'bookmark':
                        pass

                    case _:
                        raise NotImplementedError(f'Measure for {item.tag}')

            return measure, measure_marks

        def _load_measure_mark(mark_element: ET.Element) -> MeasureMark:
            pass

        def _load_note(note_item: ET.Element, divisions: int) -> (Note, int):
            """
            Returns a note described by the musicxml file and how far the measure has proceeded

            :param note_item: Note element from the musicxml file
            :param divisions: Divisions per quarter note, used to compute the note's value
            :return: The note described by the musicxml file and an integer describing how far the measure has
            proceeded, in relation to the divisions
            """
            note = Note()
            duration = 0

            # Dots is pre-set to find the notevalue more easily
            note.value.dots = len(note_item.findall('dot'))

            # Ratio is pre-set to find the notevalue more easily
            if (tm := note_item.find('time-modification')) is not None:

                for time_mod_item in tm:
                    if time_mod_item.tag == 'actual-notes':
                        note.value.ratio.actual = int(time_mod_item.text)

                    elif time_mod_item.tag == 'normal-notes':
                        note.value.ratio.normal = int(time_mod_item.text)

                    elif time_mod_item.tag == 'normal-type':
                        print(f'Setting abnormal notetype to {NoteType.from_mxml(time_mod_item.text)}')
                        note.value.notetype = NoteType.from_mxml(time_mod_item.text)

                    elif time_mod_item.tag == 'normal-dot':
                        pass  # This is accounted for in the next if-statement

                    else:
                        warnings.warn(f'Time element {time_mod_item.tag.title()} not implemented.',
                                      stacklevel=2)

                # If there are dots elements in time-modification, it should equal note.value.dots
                if (tm_dots := len(tm.findall('normal-dot'))) is not None:
                    if tm_dots != note.value.dots.value:
                        warnings.warn('Inconsistent dot values in musicxml file: count of <dots> is not equal'
                                      ' to count of <normal-dot>.', stacklevel=2)

                        # If the total <dots> is zero, then note defaults to using <normal-dot>
                        if note.value.dots.value == 0:
                            note.value.dots = tm_dots

            # Remaining note_child_elements are now checked
            for note_child in note_item:
                match note_child.tag:
                    case 'grace':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'chord':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'pitch':
                        for pitch_item in note_child:
                            if pitch_item.tag == 'alter':
                                from musicai.structure.pitch import Accidental
                                if note.pitch.alter == Accidental.NONE:
                                    # TODO: unknown if find() works
                                    note.pitch.alter = Accidental.find(int(pitch_item.text))

                                elif note.pitch.alter != Accidental.find(int(pitch_item.text)):
                                    # alter has already been set by <accidental> element, so checks if they're equal
                                    warnings.warn(f'MusicXML has inconsistent alter values for note {note_child}.',
                                                  stacklevel=2)

                            elif pitch_item.tag == 'octave':
                                note.pitch.octave = Octave.from_int(int(pitch_item.text))
                            elif pitch_item.tag == 'step':
                                note.pitch.step = Step[pitch_item.text]
                            else:
                                raise NotImplementedError(f'Pitch for {pitch_item.tag}')

                    case 'unpitched':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'rest':
                        note = Rest.to_rest(note)

                    case 'tie':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'cue':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'duration':
                        # The duration already takes into account dots and ratio, so those need to be divided out
                        # i.e.: duration == (NoteType * divisions * 4) * dots * self.ratio.normal / self.ratio.actual
                        new_notetype_value = int(note_child.text) / note.value.dots / divisions / 4 \
                                              / note.value.ratio.normal * note.value.ratio.actual
                        duration += int(note_child.text)

                        note.value.notetype = new_notetype_value

                    case 'instrument':
                        pass
                        # print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'footnote':
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

                    case 'type':
                        # TODO: implement double checking w/ the type element
                        # notetype = NoteType.from_str(note_child.text.upper())
                        pass

                    case 'accidental':
                        from musicai.structure.pitch import Accidental
                        if note.pitch.alter == Accidental.NONE:
                            note.pitch.alter = Accidental.from_mxml(note_child.text)

                        elif note.pitch.alter != Accidental.from_mxml(note_child.text):
                            # alter has already been set by <alter> element, so checks if they're equal
                            warnings.warn(f'MusicXML has inconsistent alter values for note {note_child}.',
                                          stacklevel=2)



                    case 'stem':
                        pass
                        # stem = StemType[note_child.text.upper()]
                    case 'notehead':
                        pass
                    case 'notehead-text':
                        pass
                    case 'time-staff':
                        pass
                    case 'beam':
                        pass
                    case 'notations':
                        pass
                    case 'lyric':
                        pass
                    case 'play':
                        pass
                    case 'listen':
                        pass

                    # Already taken into account
                    case 'dot':
                        pass
                    case 'time-modification':
                        pass

                    case _:
                        warnings.warn(f'"{note_child.tag.title()}" note element has not been implemented.',
                                      stacklevel=2)

                # if note_child.tag == 'beam':
                #     beam_number = 1
                #     if 'number' in note_child.attrib:
                #         beam_number = int(note_child.attrib['number'])
                #     else:
                #         raise ValueError('beam for {0}'.format(note_child.attrib))
                #     beam = Beam(beamtype=BeamType[note_child.text.upper().replace(' ', '_')], number=beam_number)
                #     beams.append(beam)
                # elif note_child.tag == 'chord':
                #     is_chord = True
                # elif note_child.tag == 'cue':
                #     print(note_child.tag, note_child.text, note_child.attrib)
                #     pass
                # elif note_child.tag == 'grace':
                #     print(note_child.tag, note_child.text, note_child.attrib)
                #     pass
                # elif note_child.tag == 'instrument':
                #     print(note_child.tag, note_child.text, note_child.attrib)
                #     pass
                # elif note_child.tag == 'lyric':
                #     lyric = Lyric()
                #     # print(item.tag, item.attrib)
                #     if 'number' in note_child.attrib:
                #         lyric.number = int(note_child.attrib['number'])
                #     if 'default-y' in note_child.attrib:
                #         lyric.y_offset = int(note_child.attrib['default-y'])
                #
                #     for lyric_item in note_child:
                #         if lyric_item.tag == 'syllabic':
                #             lyric.syllabic = SyllabicType[lyric_item.text.upper()]
                #         elif lyric_item.tag == 'text':
                #             lyric.text = lyric_item.text
                #         elif lyric_item.tag == 'extend':
                #             lyric.extend = True
                #         else:
                #             raise ValueError('lyric for {0}'.format(lyric_item.tag))
                # elif note_child.tag == 'notations':
                #     print(note_child.tag)
                #     for notation_item in note_child:
                #         # tied, arpeggiate, fermate, articulations (nested)
                #         # slur: number, placement, type
                #         # tuple: bracket
                #         print('\t', notation_item.tag, notation_item.text, notation_item.attrib)
                #         pass
                # elif note_child.tag == 'notehead':
                #     print(note_child.tag, note_child.text, note_child.attrib)
                #     pass
                #
                # elif note_child.tag == 'staff':
                #     staff = int(note_child.text)
                #     pass
                # elif note_child.tag == 'stem':
                #
                #     pass
                # elif note_child.tag == 'tie':
                #     if 'type' in note_child.attrib:
                #         tie = TieType[note_child.attrib['type'].upper()]
                # elif note_child.tag == 'time-modification':
                #     for time_mod_item in note_child:
                #         if time_mod_item.tag == 'actual-notes':
                #             ratio.actual = int(time_mod_item.text)
                #         elif time_mod_item.tag == 'normal-notes':
                #             ratio.normal = int(time_mod_item.text)
                #         elif time_mod_item.tag == 'normal-type':
                #             ratio_type = NoteType[time_mod_item.text.upper()]
                #         else:
                #             raise ValueError('time modification for {0}'.format(time_mod_item.tag))
                #     pass
                #
                # elif note_child.tag == 'voice':
                #     voice = int(note_child.text)
                # else:
                #     raise ValueError('note for {0}'.format(note_child.tag))

            # print(duration, time.divisions, time.denominator)
            # notetype, nt_exact = NoteType.find(duration / time.divisions / time.denominator)
            # print('notetype', notetype, notetype.duration, (duration / time.divisions / time.denominator), nt_exact)
            # print('tuplet', Tuplet.find(duration / time.divisions / time.denominator))

            # if is_rest:
            #     print('restxml', notevalue, notetype)
            #     note = Rest(value=notevalue)
            # elif pitch is not None:
            #     notevalue = NoteValue(notetype=notetype, dots=dots, ratio=ratio)
            #     note = Note(value=notevalue, pitch=pitch)
            #
            #     if beams:
            #         note.beams = beams
            #         # print(note.beams)
            #
            # else:
            #     print('unhandled note type??')
            #
            # if note is None:
            #     raise ValueError("note is None!!")

            print(f'Note {note} has been finished with duration {duration}!')

            return note, duration

        # process xml root
        # create element tree object
        tree = ET.parse(xml_file)

        # get root element
        root = tree.getroot()

        loaded_score = Score()
        if root.tag == 'score-partwise':
            loaded_score = _load_partwise(root)
        elif root.tag == 'score-timewise':
            # convert to timewise and then
            raise NotImplementedError('score-timewise')
        return loaded_score

    @classmethod
    def _save_part_metadata(cls, scorepart_elem: ET.Element, saved_part: Part, index: int) -> ET.Element:
        # Adds an ID attribute
        scorepart_elem.set('id', f'P{index}')
        # Set the part name
        part_name = ET.SubElement(scorepart_elem, 'part-name')
        part_name.text = saved_part.name

        return scorepart_elem

    @classmethod
    def measure_mark_mxml_type(cls, mm: MeasureMark) -> str:
        from musicai.structure.measure_mark import DynamicChangeMark

        if isinstance(mm, DynamicChangeMark):
            return mm.dynamic_change_type.name.lower()

        else:
            print('Other types of measure mark types not supported yet')
            return 'not_supported_yet'

    @classmethod
    def _save_part_measures(cls, part_elem: ET.Element, saved_part: Part, index: int) -> ET.Element:
        """
        Currently does not support overlapping measure marks yet

        :param part_elem:
        :param saved_part:
        :param index:
        :return:
        """
        measure_count = 1

        # Variables for keeping a running total of measure marks and the current time signature / clef
        s_measure_marks_to_end = []
        current_time_sig = None
        current_clef = None

        # FOR EVERY MEASURE
        for measure in saved_part.measures:
            new_measure_elem = ET.SubElement(part_elem, 'measure', {'number': f'{measure_count}'})

            # Will be used if there is a new clef or time signature
            attributes_elem = None

            # NEW TIME SIGNATURE
            if current_time_sig is not measure.time:
                current_time_sig = measure.time

                attributes_elem = ET.SubElement(new_measure_elem, 'attributes')
                time_elem = ET.SubElement(attributes_elem, 'time')

                ET.SubElement(time_elem, 'beats')
                time_elem.find('beats').text = str(measure.time.numerator)
                ET.SubElement(time_elem, 'beats-type')
                time_elem.find('beats-type').text = str(measure.time.denominator)

            # NEW CLEF
            if current_clef is not measure.clef:
                current_clef = measure.clef

                # Make the 'attributes' elem if it hasn't been made yet
                if attributes_elem is None:
                    attributes_elem = ET.SubElement(new_measure_elem, 'attributes')
                clef_elem = ET.SubElement(attributes_elem, 'clef')

                # Sign
                # TODO: must add a cleftype.to_xml() function
                ET.SubElement(clef_elem, 'sign')
                clef_elem.find('sign').text = str(measure.clef.cleftype.name)

                # Line
                ET.SubElement(clef_elem, 'line')
                clef_elem.find('line').text = str(measure.clef.line)

                # Octave change
                if int(measure.clef.octave_change) != 0:
                    ET.SubElement(clef_elem, 'clef-octave-change')
                    clef_elem.find('clef-octave-change').text = str(int(measure.clef.octave_change))

            # NOTES and MEASURE MARKS
            current_musical_pos = 0
            measure_marks_to_save = measure.measure_marks.copy()

            for s_note in measure.notes:

                # START A MEASURE MARK BEFORE THE NOTE
                for mm in measure_marks_to_save:
                    if mm.start_point <= current_musical_pos:
                        # Print the mark and remove it from the list
                        direction_elem = ET.SubElement(new_measure_elem, 'direction')

                        # TODO: Add a function to add varying mark tags depending on the type of mark
                        from musicai.structure.measure_mark import DynamicChangeMark
                        if isinstance(mm, DynamicChangeMark):
                            ET.SubElement(direction_elem, 'direction-type')
                            ET.SubElement(direction_elem.find('direction-type'), 'wedge',
                                          {'color':'#000000', 'type': MusicXML.measure_mark_mxml_type(mm)})

                        # Add it to the list of opened measure marks (so mm will later be checked to be closed)
                        s_measure_marks_to_end.append(mm)
                        measure_marks_to_save.remove(mm)

                # TODO: Currently only works for non-overlapping measure marks

                # STOP A MEASURE MARK BEFORE THE NOTE
                for mm in s_measure_marks_to_end:

                    # If the measure mark is in this measure and its end point has been reached
                    if mm.measure_span < 1 and mm.end_point <= current_musical_pos:
                        direction_elem = ET.SubElement(new_measure_elem, 'direction')

                        # TODO: Add a function to add 'STOP' tags depending on the mark-type
                        from musicai.structure.measure_mark import DynamicChangeMark
                        if isinstance(mm, DynamicChangeMark):
                            ET.SubElement(direction_elem, 'direction-type')
                            ET.SubElement(direction_elem.find('direction-type'), 'wedge',
                                          {'color': '#000000', 'type': 'stop'})

                        # The mark is discarded as now it's been implemented
                        s_measure_marks_to_end.remove(mm)

                # NOTE
                # TODO: Modularize this into a function
                note_elem = ET.SubElement(new_measure_elem, 'note', {'color': '#000000'})

                # Pitch
                pitch_elem = ET.SubElement(note_elem, 'pitch')

                ET.SubElement(pitch_elem, 'step')
                pitch_elem.find('step').text = str(s_note.pitch.step)
                ET.SubElement(pitch_elem, 'octave')
                pitch_elem.find('octave').text = str(int(s_note.pitch.octave))

                from musicai.structure.pitch import Accidental
                if s_note.pitch.alter != Accidental.NONE:
                    # TODO: Implement accidental.to_mxml() (not high priority)
                    ET.SubElement(pitch_elem, 'alter')
                    pitch_elem.find('alter').text = str(float(s_note.pitch.alter))

                # Duration
                ET.SubElement(note_elem, 'duration')
                duration_value = (s_note.value.value * 4) * s_note.division
                note_elem.find('duration').text = str(duration_value)

                # UPDATE CURRENT_MUSICAL_POSITION AND RUNNING LIST OF MEASURE MARKS
                for mm in s_measure_marks_to_end:
                    mm.measure_span -= 1
                current_musical_pos += (s_note.value.value * 4) * s_note.division

            # ADD LEFT OVER MEASURE MARKS
            if len(s_measure_marks_to_end) > 0:
                warnings.warn(f'Not all measure marks were completely added in part {saved_part}--adding them'
                              f' to the end.')

                # Identify the element of the final measure
                all_measure_count = len(saved_part.measures)
                measure_list = part_elem.findall('measure')
                assert len(measure_list) == all_measure_count
                final_measure_elem = measure_list[all_measure_count - 1]

                # Add in a stop wedge at the end for the measure mark
                from musicai.structure.measure_mark import DynamicChangeMark
                for mm in s_measure_marks_to_end:
                    # TODO: Add a function to add 'STOP' tags depending on the mark-type
                    if isinstance(mm, DynamicChangeMark):

                        ET.SubElement(final_measure_elem, 'direction-type')
                        ET.SubElement(final_measure_elem.find('direction-type'), 'wedge',
                                      {'color': '#000000', 'type': 'stop'})

        return part_elem

    @staticmethod
    def save(score: Score, xml_file: str):

        mxml_body = '<score-partwise version="4.0"><part-list></part-list>' \
                    '</score-partwise>'

        root = ET.fromstring(mxml_body)

        partlist = root.find('part-list')

        # Add a comment after the index of the partlist
        parts_divider = ET.Comment('=========================================================')
        root.insert(list(root.iter()).index(partlist) + 1, parts_divider)

        # For each part in the score, saves its information
        # TODO: Add distinctions between separator part systems, currently only works with =1 part system
        for part_system in score.systems:
            index = 1
            for part in part_system.parts:
                # Saves part metadata
                partlist_elem = ET.SubElement(partlist, 'score-part')
                partlist_elem = MusicXML._save_part_metadata(partlist_elem, part, index)

                # Saves every measure in the part
                part_elem = ET.SubElement(root, 'part', {'id': f'P{index}'})
                part_elem = MusicXML._save_part_measures(part_elem, part, index)

                # Adds a divider between every measure
                measure_divider = ET.Comment('=======================================================')
                part_elem.insert(index, measure_divider)

                # Measure number is incremented
                index += 1

        # reparsed = minidom.parseString(ET.tostring(root))
        # pretty_xml = reparsed.toprettyxml(encoding='UTF-8', standalone='no')
        # import os
        # pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])

        # with open(xml_file, 'w') as outfile:
        #     outfile.write(pretty_xml)

        tree = ET.ElementTree(root)
        ET.indent(tree, space='\t')

        tree.write(xml_file, encoding='UTF-8', xml_declaration=True)


def main():
    # file = '../../examples/mxml/Binchois.musicxml'
    # file = '../../examples/mxml/BeetAnGeSample.musicxml'
    # file = '../../examples/mxml/BrahWiMeSample.musicxml'
    # file = '../../examples/mxml/BrookeWestSample.musicxml'
    # file = '../../examples/mxml/Chant.musicxml'
    # file = '../../examples/mxml/DebuMandSample.musicxml'
    # file = '../../examples/mxml/Dichterliebe01.musicxml'
    # file = '../../examples/mxml/Echigo-Jishi.musicxml'
    # file = '../../examples/mxml/FaurReveSample.musicxml'
    # file = '../../examples/mxml/HelloWorld.musicxml'
    # file = '../../examples/mxml/HelloWorld2.musicxml'
    file = '../../examples/mxml/HelloWorld3.musicxml'
    # file = '../../examples/mxml/MahlFaGe4Sample.musicxml'
    # file = '../../examples/mxml/MozaChloSample.musicxml'
    # file = '../../examples/mxml/MozartPianoSonata.musicxml'
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # file = '../../examples/mxml/MozaVeilSample.musicxml'
    # file = '../../examples/mxml/Saltarello.musicxml'
    # file = '../../examples/mxml/SchbAvMaSample.musicxml'
    # file = '../../examples/mxml/Telemann.musicxml'

    new_file = '../../examples/mxml/new_saves/test1.musicxml'

    # Create a score with a note and dynamic change mark
    score_to_save = Score()
    score_to_save.systems[0].parts[0].measures[0].append(Note())
    from musicai.structure.measure_mark import DynamicChangeMark
    score_to_save.systems[0].parts[0].measures[0].measure_marks.append(
        DynamicChangeMark())

    print('works')

    MusicXML.save(score_to_save, new_file)

    # score = MusicXML.load(file)
    #
    # print('\n\n\n')
    #
    # score.print_measure_marks()
    # print(f'Final score: {score}')
    # score.print_measure_marks()


if __name__ == "__main__":
    main()
