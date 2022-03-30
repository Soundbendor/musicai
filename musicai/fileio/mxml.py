import xml.etree.ElementTree as ET
from datetime import date

from musicai.structure.note_mark import StemType, Beam, BeamType, TieType
from musicai.structure.clef import Clef, ClefOctave
from musicai.structure.key import ModeType, KeyType, Key
from musicai.structure.lyric import Lyric, SyllabicType
from musicai.structure.measure import Measure
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
                                        if ident_element.attrib['type'].lower() == 'composer' \
                                                and new_score.metadata.composer == '':
                                            new_score.metadata.composer = ident_element.text
                                            # TODO: If there's no 'composer' type, then the main composer is never set
                                        else:
                                            creator_tuple = (ident_element.attrib['type'], ident_element.text)
                                            new_score.metadata.creators.append(creator_tuple)

                                    else:  # the dictionary doesn't properly exist
                                        creator_tuple = ('Creator', ident_element.text)
                                        new_score.metadata.creators.append(creator_tuple)

                                case 'rights':
                                    if 'type' in ident_element.attrib.keys():  # if the type is defined
                                        new_score.metadata.append_right(ident_element.text, ident_element.attrib['type'])
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

                    case 'part-list':  # musical parts of the document
                        print(partwise_item.tag, partwise_item.text, partwise_item.attrib)  # TODO

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
            part = Part()

            if 'id' in part_item.attrib.keys():
                part.id = part_item.attrib['id']

            for item in part_item:
                print('part', part)
                if item.tag == 'measure':
                    measure = _load_measure(item, Measure(time=time, key=key))
                    # print('measure', measure)
                    part.append(measure)
                else:
                    raise NotImplementedError('part for {0}'.format(item.tag))

                # update time and key signatures, to be used future measures
                if measure.time is not None:
                    time = measure.time
                else:
                    measure.time_signature = time

                if measure.key is not None:
                    key = measure.key
                else:
                    measure.key = key

            return part

        def _load_measure(measure_element: ET.Element, measure: Measure) -> Measure:
            print('=====measure=====')
            divisions = 0
            for item in measure_element:

                match item.tag:
                    case 'attributes':
                        pass

                if item.tag == 'attributes':
                    for child in item:
                        # print(child.tag)
                        if child.tag == 'clef':
                            measure.display_clef = True
                            clef_octave = ClefOctave.NORMAL
                            clef_line = 3
                            clef_number = 0
                            clef_sign = 'G'
                            if 'number' in child.attrib:
                                clef_number = child.attrib['number']
                            for clef_item in child:
                                if clef_item.tag == 'line':
                                    clef_line = int(clef_item.text)
                                elif clef_item.tag == 'sign':
                                    clef_sign = clef_item.text
                                elif clef_item.tag == 'clef-octave-change':
                                    clef_octave = int(clef_item.text)
                                else:
                                    raise NotImplementedError('clef for {0}'.format(clef_item.tag))
                            # clef = Clef(cleftype=ClefType[sign], line=line)
                            clef = Clef(clef_sign, line=clef_line)
                        elif child.tag == 'divisions':
                            divisions = int(child.text)
                            print('div', divisions)
                        elif child.tag == 'key':
                            measure.display_key = True
                            new_key = Key()
                            for key_item in child:
                                if key_item.tag == 'fifths':
                                    new_key.keytype = KeyType.find(int(key_item.text))
                                elif key_item.tag == 'mode':
                                    new_key.modetype = ModeType[key_item.text.upper()]
                                else:
                                    raise NotImplementedError('key for {0}'.format(key_item.tag))
                            measure.key = new_key
                            print('new key', measure.key)
                        elif child.tag == 'staves':
                            print(child.tag, child.text, child.attrib)
                            pass
                        elif child.tag == 'time':

                            measure.display_time = True
                            new_time_signature = TimeSignature()
                            for time_item in child:
                                if time_item.tag == 'beats':
                                    new_time_signature.numerator = int(time_item.text)
                                elif time_item.tag == 'beat-type':
                                    new_time_signature.denominator = int(time_item.text)
                                else:
                                    raise NotImplementedError('time for {0}'.format(time_item.tag))
                            new_time_signature.divisions = divisions
                            measure.time = new_time_signature
                            print('new time', measure.time)
                        elif child.tag == 'transpose':
                            print(child.tag, child.text, child.attrib)
                            pass
                        else:
                            raise NotImplementedError('attributes for {0}'.format(child.tag))
                elif item.tag == 'backup':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'barline':
                    print('barline', item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'direction':
                    print('direction', item.tag, item.text, item.attrib)
                    for child in item:
                        print('\t', child.tag, child.attrib)
                        if child.tag == 'direction-type':
                            if 'number' in child.attrib:
                                clef_number = child.attrib['number']
                    #                            for clef_item in child:

                    pass
                elif item.tag == 'harmony':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'forward':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'note':
                    measure.append(_load_note(item, measure.time, measure.key))
                elif item.tag == 'print':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'sound':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'staff-layout':
                    print(item.tag, item.text, item.attrib)
                    pass
                else:
                    raise NotImplementedError('measure for {0}'.format(item.tag))


                # if item.tag == 'attributes':
                #     for child in item:
                #         # print(child.tag)
                #         if child.tag == 'clef':
                #             measure.display_clef = True
                #             clef_octave = ClefOctave.NORMAL
                #             clef_line = 3
                #             clef_number = 0
                #             clef_sign = 'G'
                #             if 'number' in child.attrib:
                #                 clef_number = child.attrib['number']
                #             for clef_item in child:
                #                 if clef_item.tag == 'line':
                #                     clef_line = int(clef_item.text)
                #                 elif clef_item.tag == 'sign':
                #                     clef_sign = clef_item.text
                #                 elif clef_item.tag == 'clef-octave-change':
                #                     clef_octave = int(clef_item.text)
                #                 else:
                #                     raise NotImplementedError('clef for {0}'.format(clef_item.tag))
                #             # clef = Clef(cleftype=ClefType[sign], line=line)
                #             clef = Clef(clef_sign, line=clef_line)
                #         elif child.tag == 'divisions':
                #             divisions = int(child.text)
                #             print('div', divisions)
                #         elif child.tag == 'key':
                #             measure.display_key = True
                #             new_key = Key()
                #             for key_item in child:
                #                 if key_item.tag == 'fifths':
                #                     new_key.keytype = KeyType.find(int(key_item.text))
                #                 elif key_item.tag == 'mode':
                #                     new_key.modetype = ModeType[key_item.text.upper()]
                #                 else:
                #                     raise NotImplementedError('key for {0}'.format(key_item.tag))
                #             measure.key = new_key
                #             print('new key', measure.key)
                #         elif child.tag == 'staves':
                #             print(child.tag, child.text, child.attrib)
                #             pass
                #         elif child.tag == 'time':
                #
                #             measure.display_time = True
                #             new_time_signature = TimeSignature()
                #             for time_item in child:
                #                 if time_item.tag == 'beats':
                #                     new_time_signature.numerator = int(time_item.text)
                #                 elif time_item.tag == 'beat-type':
                #                     new_time_signature.denominator = int(time_item.text)
                #                 else:
                #                     raise NotImplementedError('time for {0}'.format(time_item.tag))
                #             new_time_signature.divisions = divisions
                #             measure.time = new_time_signature
                #             print('new time', measure.time)
                #         elif child.tag == 'transpose':
                #             print(child.tag, child.text, child.attrib)
                #             pass
                #         else:
                #             raise NotImplementedError('attributes for {0}'.format(child.tag))
                # elif item.tag == 'backup':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'barline':
                #     print('barline', item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'direction':
                #     print('direction', item.tag, item.text, item.attrib)
                #     for child in item:
                #         print('\t', child.tag, child.attrib)
                #         if child.tag == 'direction-type':
                #             if 'number' in child.attrib:
                #                 clef_number = child.attrib['number']
                #     #                            for clef_item in child:
                #
                #     pass
                # elif item.tag == 'harmony':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'forward':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'note':
                #     measure.append(_load_note(item, measure.time, measure.key))
                # elif item.tag == 'print':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'sound':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # elif item.tag == 'staff-layout':
                #     print(item.tag, item.text, item.attrib)
                #     pass
                # else:
                #     raise NotImplementedError('measure for {0}'.format(item.tag))
            return measure

        def _load_note(note_item, time, key):
            # print('time=', time)
            note = None
            pitch = None
            is_rest, is_chord = False, False
            last_chord = None
            dots = 0
            duration = -1
            accidental = Accidental.NONE
            notetype = NoteType.NONE
            voice = 0
            staff = 0
            stem = StemType.NONE
            tie = None
            lyric = None
            beams = []
            ratio = Ratio()

            for item in note_item:
                if item.tag == 'accidental':
                    accidental = Accidental[item.text.upper()]
                elif item.tag == 'beam':
                    beam_number = 1
                    if 'number' in item.attrib:
                        beam_number = int(item.attrib['number'])
                    else:
                        raise ValueError('beam for {0}'.format(item.attrib))
                    beam = Beam(beamtype=BeamType[item.text.upper().replace(' ', '_')], number=beam_number)
                    beams.append(beam)
                elif item.tag == 'chord':
                    is_chord = True
                elif item.tag == 'cue':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'dot':
                    dots += 1
                elif item.tag == 'duration':
                    duration = int(item.text)
                    print('duration', item.tag, item.text)
                elif item.tag == 'grace':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'instrument':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'lyric':
                    lyric = Lyric()
                    # print(item.tag, item.attrib)
                    if 'number' in item.attrib:
                        lyric.number = int(item.attrib['number'])
                    if 'default-y' in item.attrib:
                        lyric.y_offset = int(item.attrib['default-y'])

                    for lyric_item in item:
                        if lyric_item.tag == 'syllabic':
                            lyric.syllabic = SyllabicType[lyric_item.text.upper()]
                        elif lyric_item.tag == 'text':
                            lyric.text = lyric_item.text
                        elif lyric_item.tag == 'extend':
                            lyric.extend = True
                        else:
                            raise ValueError('lyric for {0}'.format(lyric_item.tag))
                elif item.tag == 'notations':
                    print(item.tag)
                    for notation_item in item:
                        # tied, arpeggiate, fermate, articulations (nested)
                        # slur: number, placement, type
                        # tuple: bracket
                        print('\t', notation_item.tag, notation_item.text, notation_item.attrib)
                        pass
                elif item.tag == 'notehead':
                    print(item.tag, item.text, item.attrib)
                    pass
                elif item.tag == 'pitch':
                    pitch = Pitch()
                    for pitch_item in item:
                        if pitch_item.tag == 'alter':
                            pitch.alter = Accidental.find(int(pitch_item.text))
                        elif pitch_item.tag == 'midi':
                            pitch.midi = int(pitch_item.text)
                        elif pitch_item.tag == 'octave':
                            pitch.octave = Octave.from_int(int(pitch_item.text))
                        elif pitch_item.tag == 'step':
                            pitch.step = Step[pitch_item.text]
                        else:
                            raise ValueError('pitch for {0}'.format(pitch_item.tag))

                elif item.tag == 'rest':
                    is_rest = True
                elif item.tag == 'staff':
                    staff = int(item.text)
                    pass
                elif item.tag == 'stem':
                    stem = StemType[item.text.upper()]
                    pass
                elif item.tag == 'tie':
                    if 'type' in item.attrib:
                        tie = TieType[item.attrib['type'].upper()]
                elif item.tag == 'time-modification':
                    for time_mod_item in item:
                        if time_mod_item.tag == 'actual-notes':
                            ratio.actual = int(time_mod_item.text)
                        elif time_mod_item.tag == 'normal-notes':
                            ratio.normal = int(time_mod_item.text)
                        elif time_mod_item.tag == 'normal-type':
                            ratio_type = NoteType[time_mod_item.text.upper()]
                        else:
                            raise ValueError('time modification for {0}'.format(time_mod_item.tag))
                    pass
                elif item.tag == 'type':
                    # print('notettypexml', item.text.upper())
                    notetype = NoteType.from_str(item.text.upper())
                elif item.tag == 'voice':
                    voice = int(item.text)
                else:
                    raise ValueError('note for {0}'.format(item.tag))

            # print(duration, time.divisions, time.denominator)
            # notetype, nt_exact = NoteType.find(duration / time.divisions / time.denominator)
            # print('notetype', notetype, notetype.duration, (duration / time.divisions / time.denominator), nt_exact)
            # print('tuplet', Tuplet.find(duration / time.divisions / time.denominator))

            notevalue = NoteValue.find(duration / time.divisions / time.denominator)
            if is_rest:
                print('restxml', notevalue, notetype)
                note = Rest(value=notevalue)
            elif pitch is not None:
                notevalue = NoteValue(notetype=notetype, dots=dots, ratio=ratio)
                note = Note(value=notevalue, pitch=pitch)

                if is_chord:
                    print('CHORD')

                if beams:
                    note.beams = beams
                    # print(note.beams)

            else:
                print('unhandled note type??')

            if note is None:
                raise ValueError("note is None!!")

            return note

        # process xml root
        # create element tree object
        tree = ET.parse(xml_file)

        # get root element
        root = tree.getroot()

        score = Score()
        if root.tag == 'score-partwise':
            score = _load_partwise(root)
        elif root.tag == 'score-timewise':
            # convert to timewise and then
            raise NotImplementedError('score-timewise')
        return score


if __name__ == "__main__":
    # file = '../../examples/mxml/Binchois.musicxml'
    # file = '../../examples/mxml/BeetAnGeSample.musicxml'
    # file = '../../examples/mxml/BrahWiMeSample.musicxml'
    # file = '../../examples/mxml/BrookeWestSample.musicxml'
    # file = '../../examples/mxml/Chant.musicxml'
    # file = '../../examples/mxml/DebuMandSample.musicxml'
    # file = '../../examples/mxml/Dichterliebe01.musicxml'
    # file = '../../examples/mxml/Echigo-Jishi.musicxml'
    file = '../../examples/mxml/FaurReveSample.musicxml'
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
