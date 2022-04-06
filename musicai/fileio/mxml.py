import warnings
import xml.etree.ElementTree as ET
from typing import Union

from musicai.structure.note_mark import StemType, Beam, BeamType, TieType
from musicai.structure.clef import Clef, ClefOctave
from musicai.structure.key import ModeType, KeyType, Key
from musicai.structure.lyric import Lyric, SyllabicType
from musicai.structure.measure import Measure
from musicai.structure.measure_mark import MeasureMark
from musicai.structure.note import NoteType, Ratio, NoteValue, Rest, Note
from musicai.structure.pitch import Accidental, Pitch, Octave, Step
from musicai.structure.score import Score, PartSystem, Part
from musicai.structure.time import TimeSignature


class MusicXML:

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
                                    print('encoding registered, ', ident_element.text)  # TODO

                                case 'source':  # source of the encoded music
                                    new_score.metadata.source = ident_element.text

                                case 'relation':  # related resource to the encoded music
                                    print('relation registered, ', ident_element.text)  # TODO

                                case 'miscellaneous':  # custom metadata
                                    print('misc info registered, ', ident_element.text)  # TODO

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
                                case _: NotImplementedError(f'Unknown element \"{work_element.tag}\" under the work'
                                                            f'element.')

                    case 'default':  # score-wide scaling defaults
                        print(partwise_item.tag, partwise_item.text, partwise_item.attrib)  # TODO

                    case 'credit':  # appearence of information on the front pages
                        print(partwise_item.tag, partwise_item.text, partwise_item.attrib)  # TODO

                    case 'part-list':  # titles and info about parts of the document
                        print(partwise_item.tag, partwise_item.text, partwise_item.attrib)  # TODO
                        # TODO: Make this go AFTER <parts>?

                    case 'part':  # parts which contain measures
                        print(partwise_item.tag, partwise_item.text, partwise_item.attrib)
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
            measure_marks = list[MeasureMark]

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
                print('part', part)
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

            # appends remaining unresolved measure marks
            for mm in measure_marks:
                mm.end_time = 0
                part.measures[mm.measure_index].measure_marks.append(mm)  # TODO: find a way to update the measure_index

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

            # TODO: update measure_marks when a <direction> element is read

            current_musical_location = 0  # incremented as more notes are added

            for item in measure_element:

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
                        print(f'{item.tag.title()} in Measure has not been implemented yet')

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
                                            if wedge_type == 'crescendo' or wedge_type == 'decrescendo':
                                                dcm = DynamicChangeMark(current_musical_location, 0, wedge_type,
                                                                        hairpin=True, divisions=divisions)
                                                # ===== for multi-spanning measures =====
                                                dcm.measure_index = measure_index
                                                dcm.number = dir_type.get('number')
                                                # ========
                                                measure_marks.append(dcm)

                                            elif wedge_type == 'stop':

                                                if dir_type.get('number') is not None:
                                                    # loops until it finds the corresponding measure mark
                                                    for mm in measure_marks:
                                                        if mm.number == dir_type.get('number') and \
                                                                isinstance(mm, DynamicChangeMark):

                                                            if mm.measure_span == 0:
                                                                measure.measure_marks.append(mm)
                                                            else:
                                                                print(f'Multiple measure marks not implemented yet')
                                                                # Add the measure to a previous one, based on its index
                                                                pass

                                                            # TODO: now remove the list item

                                                            break
                                                        # No way of checking if the loop failed so far

                                                else:
                                                    for mm in measure_marks:
                                                        if isinstance(mm, DynamicChangeMark):
                                                            measure.measure_marks.append(mm)

                                            elif wedge_type == 'continue':
                                                # Not sure if this attribute means anything for this project
                                                pass
                                            else:
                                                warnings.warn(f'Measure mark wedge of value {wedge_type} is not '
                                                              f'supported.', stacklevel=2)

                                        case '':
                                            pass
                                        case _:
                                            print(f'{dir_type.tag.title()} in Measure has not been implemented yet')

                            elif dir_child.tag == 'staff':
                                print(f'{dir_child.tag.title()} in Measure has not been implemented yet')
                            else:
                                print(f'{dir_child.tag.title()} in Measure has not been implemented yet')

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

            # Measure marks that have not been resolved yet are noted to exist for another measure
            for mm in measure_marks:
                if mm is MeasureMark:
                    mm.measure_span += 1

            return measure, measure_marks

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
                        print(f'"{note_child.tag.title()}" note element has not been implemented yet.')

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
                        stem = StemType[note_child.text.upper()]
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


if __name__ == "__main__":
    # file = '../../examples/mxml/Binchois.musicxml'
    # file = '../../examples/mxml/BeetAnGeSample.musicxml'
    # file = '../../examples/mxml/BrahWiMeSample.musicxml'
    # file = '../../examples/mxml/BrookeWestSample.musicxml'
    # file = '../../examples/mxml/Chant.musicxml'
    # file = '../../examples/mxml/DebuMandSample.musicxml'
    # file = '../../examples/mxml/Dichterliebe01.musicxml'
    # file = '../../examples/mxml/Echigo-Jishi.musicxml'
    #   file = '../../examples/mxml/FaurReveSample.musicxml'
    file = '../../examples/mxml/HelloWorld.musicxml'
    # file = '../../examples/mxml/MahlFaGe4Sample.musicxml'
    # file = '../../examples/mxml/MozaChloSample.musicxml'
    # file = '../../examples/mxml/MozartPianoSonata.musicxml'
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # file = '../../examples/mxml/MozaVeilSample.musicxml'
    # file = '../../examples/mxml/Saltarello.musicxml'
    # file = '../../examples/mxml/SchbAvMaSample.musicxml'
    # file = '../../examples/mxml/Telemann.musicxml'
    score = MusicXML.load(file)

    print('\n\n\n')
    print('Printing...', score)

    print('FILLER')

    print(score.systems[0])

    # TODO: Sort out typing in score.py to make evything more clear