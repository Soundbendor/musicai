import copy
import warnings
import xml.etree.ElementTree as ET

import numpy as np
from typing import Union

from musicai.structure.note_mark import StemType, Beam, BeamType, TieType, ArticulationType, OrnamentType, SlurType, \
    NoteheadType, Notehead
from musicai.structure.clef import Clef, ClefOctave, ClefType
from musicai.structure.key import ModeType, KeyType, Key
from musicai.structure.lyric import Lyric, SyllabicType
from musicai.structure.measure import Measure, Barline, BarlineType, BarlineLocation, Transposition
from musicai.structure import measure_mark
from musicai.structure.measure_mark import MeasureMark, InstantaneousMeasureMark
from musicai.structure.note import NoteType, Ratio, NoteValue, Rest, Note, NoteGroup
from musicai.structure.pitch import Accidental, Pitch, Octave, Step
from musicai.structure.score import Score, PartSystem, Part, GroupingSymbol
from musicai.structure.time import TimeSignature, TimeSymbolType, Tempo


class XMLConversion:
    from musicai.structure.measure_mark import HairpinType
    from musicai.structure.note_mark import Articulation, ArticulationType, Notehead, NoteheadType
    from musicai.structure.measure import BarlineType, Barline, BarlineLocation
    from musicai.structure.score import GroupingSymbol

    # -----------
    # Class Methods
    # -----------
    @classmethod
    def barline_to_barstyle(cls, value: Union[Barline, BarlineType]) -> str:
        if isinstance(value, list):
            warnings.warn(f'Does not support multiple measures yet.', stacklevel=2)
            return ''

        elif isinstance(value, Barline):
            value = value.barlinetype

        # 'if' instead of 'elif' here is purposeful--Barline leads into BarlineType
        if isinstance(value, BarlineType):
            match value:
                case BarlineType.NONE:
                    return 'none'
                case BarlineType.SHORT:
                    return 'short'
                case BarlineType.TICK:
                    return 'tick'
                case BarlineType.REGULAR:
                    return 'regular'
                case BarlineType.DOUBLE:
                    return 'light-light'
                case BarlineType.FINAL:
                    return 'light-heavy'
                case BarlineType.REVERSE_FINAL:
                    return 'heavy-light'
                case BarlineType.HEAVY:
                    return 'heavy'
                case BarlineType.DOUBLE_HEAVY:
                    return 'heavy-heavy'
                case BarlineType.DASHED:
                    return 'dashed'
                case BarlineType.DOTTED:
                    return 'dotted'
                case BarlineType.INVISIBLE:
                    return 'none'
                case _:
                    warnings.warn(f'Barline {value} has a value invalid with mxml. Defaulting to invisible barline.',
                                  stacklevel=2)
                    return 'none'

        else:
            raise TypeError(f'Cannot generate an mxml barline from type {type(value)}.')

    @classmethod
    def barline_to_mxml(cls, value: Union[Barline, BarlineType]) -> ET.Element:
        """
        Currenty only used for right-sided barlines, however has functionality for left-sided
        repeats

        :param value:
        :return:
        """
        if not isinstance(value, Union[Barline, BarlineType]):
            raise TypeError(f'Cannot make a mxml barline element from type {type(value)}')

        bl_elem = ET.Element('barline')

        # Sets the location if applicable and defines btype
        if isinstance(value, Barline):
            bl_elem.attrib['location'] = value.barlinelocation.name.lower()
            btype = value.barlinetype
        else:
            btype = value

        # If this is irregular repeat barlines, does them specially
        if btype == BarlineType.LEFT_REPEAT or btype == BarlineType.RIGHT_REPEAT:

            # Describes if this is FINAL or REVERSE FINAL
            if isinstance(value, Barline):
                # BARLINE
                if value.barlinelocation == BarlineLocation.LEFT:
                    ET.SubElement(bl_elem, 'bar-style')
                    bl_elem.find('bar-style').text = 'heavy-light'
                else:
                    ET.SubElement(bl_elem, 'bar-style')
                    bl_elem.find('bar-style').text = 'light-heavy'
            else:
                # BARLINETYPE
                if value == BarlineType.LEFT_REPEAT:
                    ET.SubElement(bl_elem, 'bar-style')
                    bl_elem.find('bar-style').text = 'heavy-light'
                else:
                    ET.SubElement(bl_elem, 'bar-style')
                    bl_elem.find('bar-style').text = 'light-heavy'

            ET.SubElement(bl_elem, 'repeat')
            if btype == BarlineType.LEFT_REPEAT:
                bl_elem.find('repeat').attrib['direction'] = 'forward'
            else:
                bl_elem.find('repeat').attrib['direction'] = 'backward'

            return bl_elem

        # This is a non-repeat barline: Deal with accordingly
        ET.SubElement(bl_elem, 'bar-style')
        bl_elem.find('bar-style').text = XMLConversion.barline_to_barstyle(value)
        return bl_elem

    @classmethod
    def barlinetype_from_mxml(cls, value: str) -> BarlineType:
        if not isinstance(value, str):
            return BarlineType.NONE

        match value:
            case 'dashed':
                return BarlineType.DASHED
            case 'dotted':
                return BarlineType.DOTTED
            case 'heavy':
                return BarlineType.HEAVY
            case 'heavy-heavy':
                return BarlineType.DOUBLE_HEAVY
            case 'heavy-light':
                return BarlineType.REVERSE_FINAL
            case 'light-heavy':
                return BarlineType.FINAL
            case 'light-light':
                return BarlineType.DOUBLE
            case 'none':
                return BarlineType.NONE
            case 'regular':
                return BarlineType.REGULAR
            case 'short':
                return BarlineType.SHORT
            case 'tick':
                return BarlineType.TICK
            case _:
                return BarlineType.NONE

    @classmethod
    def barlinelocation_from_mxml(cls, value: str) -> BarlineLocation:
        if not isinstance(value, str):
            return BarlineLocation.NONE

        match value:
            case 'right':
                return BarlineLocation.RIGHT
            case 'left':
                return BarlineLocation.LEFT
            case 'middle':
                return BarlineLocation.MIDDLE
            case _:
                return BarlineLocation.NONE

    @classmethod
    def barline_from_mxml(cls, bl_elem: ET.Element) -> Barline:
        new_bl = Barline()

        # Barline location
        if 'location' in bl_elem.attrib.keys():
            new_bl.barlinelocation = XMLConversion.barlinelocation_from_mxml(bl_elem.get('location'))

        # Barline type
        if bl_elem.find('repeat') is not None:
            # Repeating barline
            if bl_elem.find('repeat').get('direction') == 'forward':
                new_bl.barlinetype = BarlineType.LEFT_REPEAT
            else:
                new_bl.barlinetype = BarlineType.RIGHT_REPEAT

        elif bl_elem.find('bar-style') is not None:
            # Non-repeating barline
            new_bl.barlinetype = XMLConversion.barlinetype_from_mxml(bl_elem.find('bar-style').text)

        # For now, single barline type is supported
        print(f'NEW BARLINE: {new_bl.barlinelocation}, {new_bl.barlinetype}')
        return new_bl

    @classmethod
    def time_symbol_type_from_mxml(cls, time_elem: ET.Element) -> TimeSymbolType:
        """
        Given an element, reports what the time signature type would be.

        :param time_elem:
        :return:
        """
        if not isinstance(time_elem, ET.Element):
            raise TypeError(f'Cannot find a time symbol type from {time_elem} of type {type(time_elem)}.')

        match time_elem.get('symbol'):
            case 'normal':
                return TimeSymbolType.NORMAL
            case 'common':
                return TimeSymbolType.COMMON
            case 'cut':
                return TimeSymbolType.CUT
            case 'note':
                return TimeSymbolType.NOTE
            case 'dotted-note':
                return TimeSymbolType.DOTTED_NOTE
            case 'single-number':
                return TimeSymbolType.SINGLE
            case _:
                return TimeSymbolType.NORMAL

    @classmethod
    def time_symbol_type_to_mxml(cls, time: TimeSignature) -> str:
        """
        Given a time signature, returns the string which represents that time signature

        :param time:
        :return:
        """

        if not isinstance(time, TimeSignature):
            raise TypeError(f'Cannot construct a time symbol type string from {time} of type {type(time)}.')

        if time.timesymboltype == TimeSymbolType.SINGLE:
            return 'single-number'
        else:
            return time.timesymboltype.name.lower().replace('_', '-')

    @classmethod
    def clef_to_mxml(cls, clef: Clef, clef_number: int = 1) -> ET.Element:
        """
        Given a clef object, returns its represenation as a clef object with subelements <sign>, <line>,
        and <clef-octave-change>

        :param clef:
        :param clef_number:
        :return:
        """
        if not isinstance(clef, Clef):
            raise TypeError(f'Cannot make a mxml clef element from {clef} of type {type(clef)}.')

        clef_elem = ET.Element('clef', {'number': f'{clef_number}'})

        # SIGN
        ET.SubElement(clef_elem, 'sign')
        sign_text = ''
        match clef.cleftype:
            case ClefType.NONE:
                sign_text = 'none'
            case ClefType.F:
                sign_text = 'F'
            case ClefType.C:
                sign_text = 'C'
            case ClefType.G:
                sign_text = 'G'
            case ClefType.PERCUSSION:
                sign_text = 'percussion'
            case ClefType.TAB4 | ClefType.TAB6:
                sign_text = 'TAB'
            case _:
                sign_text = 'none'
        clef_elem.find('sign').text = sign_text

        # LINE
        ET.SubElement(clef_elem, 'line')
        clef_elem.find('line').text = str(clef.line)

        # OCTAVE CHANGE
        if int(clef.octave_change) != 0:
            ET.SubElement(clef_elem, 'clef-octave-change')
            clef_elem.find('clef-octave-change').text = str(int(clef.octave_change))

        return clef_elem

    @classmethod
    def notetype_to_mxml(cls, value: Union[Note, NoteValue, NoteType]) -> str:
        """
        Returns a string that would be used for the text in a note's <type> element

        :param value: The note, value, or notetype to be converted to note-type-value. If a notetype is passed in,
        it should have already been adjusted according to the ratio's normal value
        :return: A string for mxml note-type-value. Returns an empty string '' if no valid value exists
        """
        if isinstance(value, Note):
            value = value.value.get_ratiod_notetype()

        if isinstance(value, NoteValue):
            value = value.get_ratiod_notetype()

        if isinstance(value, NoteType):
            match value:
                # Allowed mxml values
                case NoteType.ONE_THOUSAND_TWENTY_FOURTH:
                    return '1024th'
                case NoteType.FIVE_HUNDRED_TWELFTH:
                    return '512th'
                case NoteType.TWO_FIFTY_SIXTH:
                    return '256th'
                case NoteType.ONE_TWENTY_EIGHTH:
                    return '128th'
                case NoteType.SIXTY_FOURTH:
                    return '64th'
                case NoteType.THIRTY_SECOND:
                    return '32nd'
                case NoteType.SIXTEENTH:
                    return '16th'
                case NoteType.EIGHTH:
                    return 'eighth'
                case NoteType.QUARTER:
                    return 'quarter'
                case NoteType.HALF:
                    return 'half'
                case NoteType.WHOLE:
                    return 'whole'
                case NoteType.DOUBLE:
                    return 'breve'
                case NoteType.LONG:
                    return 'long'
                case NoteType.LARGE:
                    return 'maxima'

                # Unallowed mxml values
                case NoteType.TWO_THOUSAND_FORTY_EIGHTH:
                    return '2048th'
                case NoteType.FOUR_THOUSAND_NINETY_SIXTH:
                    return '4096th'

                # Default value is nothing
                case _:
                    return ''

        else:
            raise TypeError(f'Cannot make xmxl note-type-value from type {type(value)}.')

    @classmethod
    def in_prev_notegroup(cls, note: ET.Element) -> bool:
        """
        Tells if a <note> element is supposed to be a part of a previous note group.

        :param note:
        :return: True if the note contains a <chord> element
        """
        if not isinstance(note, ET.Element):
            raise TypeError(f'Cannot check if type {type(note)} is in the previous notegroup.')

        if note.find('chord') is not None:
            return True
        else:
            return False

    @classmethod
    def ratio_to_mxml(cls, saved_note: Note) -> ET.Element:
        """
        Based on the passed in note, returns an appropriate <time-modification> element
        TODO: Add dot capabilities

        :param saved_note:
        :return:
        """

        if not isinstance(saved_note, Note):
            raise TypeError(f'Cannot make a <time-modification> element from type {type(saved_note)}.')

        tm_elem = ET.Element('time-modification')

        ET.SubElement(tm_elem, 'actual-notes')
        tm_elem.find('actual-notes').text = str(saved_note.value.ratio.actual)

        ET.SubElement(tm_elem, 'normal-notes')
        tm_elem.find('normal-notes').text = str(saved_note.value.ratio.normal)

        # <normal-type> and <normal-dot> not implemented yet
        return tm_elem

    @classmethod
    def stemtype_from_mxml(cls, stem_elem: ET.Element) -> StemType:
        """
        Takes in a <stem> element from <note> to return a StemType

        :param stem_elem:
        :return:
        """

        # Defaults to up
        if not isinstance(stem_elem, ET.Element):
            return StemType.UP

        if stem_elem.text.upper() in [st.name for st in StemType]:
            # print(f'-!-!-Made Stemtype{StemType[stem_elem.text.upper()].name} from text {stem_elem.text}!')
            return StemType[stem_elem.text.upper()]
        else:
            raise ValueError(f'Cannot make a stem from stemtype {stem_elem.text}.')

    @classmethod
    def stemtype_to_mxml(cls, value: StemType) -> ET.Element:
        """
        Takes in a StemType and returns it as a <stem> element used for <note> elements

        :param value:
        :return:
        """

        st_elem = ET.Element('stem')

        # Defaults to up
        if not isinstance(value, StemType):
            st_elem.text = 'up'
        else:
            st_elem.text = value.name.lower()

        return st_elem

    @classmethod
    def beam_from_mxml(cls, beam_elem: ET.Element) -> Beam | None:
        bt_name = beam_elem.text.replace(' ', '_').upper()

        if bt_name not in [bt_enum.name for bt_enum in BeamType]:
            return None

        bt = BeamType[bt_name]
        b_num = beam_elem.get('number')

        if b_num is not None:
            return Beam(beamtype=bt, number=int(b_num))
        else:
            return Beam(beamtype=bt)

    @classmethod
    def beam_to_mxml(cls, beam: Beam) -> ET.Element:

        beam_elem = ET.Element('beam', {'number': f'{beam.number}'})
        beam_elem.text = str(beam.beamtype).replace('_', ' ').lower()

        return beam_elem

    @classmethod
    def notehead_from_mxml(cls, nh_elem: ET.Element) -> Notehead:
        """
        From the <notehead> mxml element, returns an object of the Notehead class

        :param nh_elem:
        :return:
        """
        if not isinstance(nh_elem, ET.Element):
            raise TypeError(f'Cannot make a notehead from {nh_elem} of type {type(nh_elem)}.')

        notehead_name = nh_elem.text.upper().replace(' ', '_').replace('-', '_')

        if notehead_name == 'X':
            return Notehead(notehead_type=NoteheadType.CROSSHEAD)

        elif notehead_name in [nht.name for nht in NoteheadType]:
            return Notehead(notehead_type=NoteheadType[notehead_name])

        else:
            raise ValueError(f'Cannot make a notehead type from mxml element with text {nh_elem.text}.')

    @classmethod
    def notehead_to_mxml(cls, nh: Notehead) -> ET.Element:
        """
        Given a notehead nh, returns its <notehead> mxml element

        :param nh:
        :return:
        """
        nh_elem = ET.Element('notehead')

        if nh.notehead_type.name == 'CROSSHEAD':
            nh_elem.text = 'x'

        else:
            nh_elem.text = nh.notehead_type.name.lower().replace('circle_x', 'circle-x').replace('_', ' ')

        return nh_elem

    @classmethod
    def lyric_from_mxml(cls, lyric_elem: ET.Element) -> Lyric:
        """
        Given a mxml <lyric> element, returns a lyric object. Currently, does not support ellisions or multi-text
        lyrics.

        :param lyric_elem:
        :return:
        """
        if not isinstance(lyric_elem, ET.Element):
            raise TypeError(f'Cannot make a Lyric out of {lyric_elem} of type {type(lyric_elem)}.')

        lyr = Lyric()

        for lyr_child in lyric_elem:

            if lyr_child.tag == 'syllabic':
                lyr.syllabic = SyllabicType[lyr_child.text.upper()]

            elif lyr_child.tag == 'text':
                lyr.text = lyr_child.text

            elif lyr_child.tag == 'ellision':
                # Be aware, there may be multiple syllabic and text elements!
                pass

            elif lyr_child.tag == 'extend':
                lyr.extends = True

            else:
                # Remaining tags not supported yet
                pass

        return lyr

    @classmethod
    def lyric_to_mxml(cls, lyr: Lyric) -> ET.Element:
        """
        Given a lyric object, returns a mxml <lyric> element. Currently, does not support ellisions or multi-text
        lyrics.

        :param lyr:
        :return:
        """
        lyric_elem = ET.Element('lyric')

        # SINGLE SYLLABIC
        if lyr.syllabic != SyllabicType.NONE:
            ET.SubElement(lyric_elem, 'syllabic')
            lyric_elem.find('syllabic').text = lyr.syllabic.name.lower()

        # SINGLE TEXT
        ET.SubElement(lyric_elem, 'text')
        lyric_elem.find('text').text = lyr.text

        # SINGLE EXTEND
        if lyr.extends:
            ET.SubElement(lyric_elem, 'extend')

        return lyric_elem

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

    @classmethod
    def note_mark_from_mxml(cls, marking: ET.Element) -> object:
        match marking.tag:

            case 'tied':
                if marking.get('type') == 'start':
                    return TieType.START
                elif marking.get('type') == 'continue':
                    return TieType.CONTINUE
                # elif marking.get('type') == 'let-ring':
                else:
                    return TieType.STOP

            case 'slur':
                if marking.get('type') == 'start':
                    return SlurType.START
                elif marking.get('type') == 'continue':
                    return SlurType.CONTINUE
                else:
                    return SlurType.STOP

            case 'accent':
                return ArticulationType.ACCENT
            case 'staccato':
                return ArticulationType.STACCATO

            case 'turn':
                return OrnamentType.TURN

            case _:
                print(f'Articulation type {marking.tag} not supported yet.')
                return None

    @classmethod
    def notations_order_key(cls, notat_child: ET.Element) -> int:
        """
        Each child the <notation> element from <note> must be in a specified order. This is used as a key to determine
        what the child element's order should be

        :param notat_child:
        :return:
        """

        # Magnitude represents the maximum spacing between elements, i.e. how many elements of one type exist before
        # they go beyond the key, and it may no longer work
        magnitude = 8

        match notat_child.tag[0:4]:
            case 'foot':
                return 0 * magnitude
            case 'leve':
                return 1 * magnitude
            case 'tied':
                return 2 * magnitude
            case 'slur':
                return 3 * magnitude
            case 'tupl':
                return 4 * magnitude
            case 'glis':
                return 5 * magnitude
            case 'slid':
                return 6 * magnitude
            case 'orna':
                return 7 * magnitude
            case 'tech':
                return 8 * magnitude
            case 'arti':
                return 9 * magnitude
            case 'dyna':
                return 10 * magnitude
            case 'ferm':
                return 11 * magnitude
            case 'arpe':
                return 12 * magnitude
            case 'non-':
                return 13 * magnitude
            case 'acci':
                return 14 * magnitude
            case 'othe':
                return 15 * magnitude

            case _:
                return 16 * magnitude

    @classmethod
    def grouping_symbol_from_mxml(cls, gs_elem: ET.Element) -> GroupingSymbol:
        """
        Uses the <group-symbol> element to determine the grouping symbol

        :param gs_elem:
        :return:
        """
        if not isinstance(gs_elem, ET.Element):
            return GroupingSymbol.NONE

        match gs_elem.text.lower():
            case 'none':
                return GroupingSymbol.NONE
            case 'brace':
                return GroupingSymbol.BRACE
            case 'bracket':
                return GroupingSymbol.BRACKET
            case 'line':
                return GroupingSymbol.LINE
            case 'square':
                return GroupingSymbol.SQUARE
            case _:
                return GroupingSymbol.NONE

    @classmethod
    def grouping_symbol_to_mxml(cls, gs: GroupingSymbol) -> str:
        """
        Makes the text for the <group-symbol> element

        :param gs:
        :return:
        """
        if not isinstance(gs, GroupingSymbol):
            return ''

        if GroupingSymbol is GroupingSymbol.NONE:
            return ''

        else:
            return gs.name.lower()


class MusicXML:
    # -----------
    # Class Methods
    # -----------
    @classmethod
    def _load_partwise(cls, loaded_root: ET.Element) -> Score:
        """
        Parses a partwise mxml file into a score, partsystem, part, measure, and note.

        Currently, only one tempo is supported in the Score class. This tempo is added at the beginning of this
        function. Only reads one tempo from the top of the score.

        :param loaded_root:
        :return:
        """
        new_score = Score()

        # Finds the first tempo marking and sets tempo
        # TODO: Construct vertical beatmap and remove this
        for direction in loaded_root.find('part').find('measure').findall('direction'):
            if (metronome := direction.find('direction-type').find('metronome')) is not None:
                per_minute = int(metronome.find('per-minute').text)
                beat_unit = NoteType.from_mxml(metronome.find('beat-unit').text)
                new_score.tempo = Tempo(per_minute, beat_unit)

        # Used when new parts should be added to the same part system
        currently_grouping_parts: bool = False

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
                            case _:
                                warnings.warn(f'Unknown element \"{work_element.tag}\" under the work '
                                              f'element.', stacklevel=2)

                case 'defaults':  # score-wide scaling defaults
                    print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')  # TODO

                case 'credit':  # appearence of information on the front pages
                    print(f'{partwise_item.tag}, {partwise_item.attrib}, unused')  # TODO

                case 'part-list':  # Sets information for the partsystem

                    new_part_system = None
                    # A running list of grouping symbols
                    nested_grouping_symbols: list[GroupingSymbol] = []

                    for part_list_elem in partwise_item:

                        # GROUP PARTS INTO PART SYSTEMS
                        if part_list_elem.tag == 'part-group':

                            # New part group
                            if part_list_elem.get('type') == 'start':
                                currently_grouping_parts = True
                                new_part_system = PartSystem()

                                # Records what this grouping symbol is
                                if (pg_child := part_list_elem.find('group-symbol')) is not None:
                                    nested_grouping_symbols.append(XMLConversion.grouping_symbol_from_mxml(pg_child))
                                else:
                                    nested_grouping_symbols.append(GroupingSymbol.NONE)

                                print(f'JUST MADE IT, NEW GROUPING SYMBOL LIST:{nested_grouping_symbols}')
                                new_score.append(new_part_system)

                            # Assigns the grouping symbol
                            elif part_list_elem.get('type') == 'stop':
                                currently_grouping_parts = False

                                # Based on the part system, adds in the latest grouping symbol.

                                print(f'GOT TO HERE, GROUPING SYMBOL LIST:{nested_grouping_symbols}')

                                # If the latest partsystem has only 1 part, apply the symbol to the part
                                if len(new_part_system.parts) == 1:
                                    new_score.systems[-1].parts[0].grouping_symbol = nested_grouping_symbols.pop()

                                # Otherwise, there are more than 1 parts and the symbol should apply to the whole system
                                else:
                                    new_score.systems[-1].grouping_symbol = nested_grouping_symbols.pop()

                            else:
                                pass

                        # DECLARE A NEW PART
                        elif part_list_elem.tag == 'score-part':
                            new_part = Part()

                            # Set part information
                            for pl_child in part_list_elem:
                                if pl_child.tag == 'part-name':
                                    new_part.name = pl_child.text
                                else:
                                    pass

                            # Add the part to the score
                            if currently_grouping_parts:
                                # Add this to the most recent part system
                                new_score.append_to_latest_partsystem(new_part)
                            else:
                                # Make a new part system
                                new_part_system = PartSystem()
                                new_part_system.append(new_part)
                                new_score.append(new_part_system)

                case 'part':  # Parts which contain measures
                    pass

                case _:
                    raise NotImplementedError(f'Unknown element \"{partwise_item.tag}\" in musicxml file.')

        # For every part element, parse its information
        for part_elem in loaded_root.findall('part'):
            # Finds the part's index
            part_index = int(''.join(c for c in part_elem.get('id') if c != 'P'))

            print(f'============================================')
            print(f'ATTEMPING TO LOAD PART INDEX {part_index}')
            print(f'============================================')

            # Gets the existing part to save the information that was already set
            to_load = new_score.get_part_by_mxml_index(part_index)

            # Loads the part's information
            new_score.set_part_by_mxml_index(MusicXML._load_part(part_elem, to_load), part_index)

        return new_score

    @classmethod
    def _get_staff_count(cls, part_elem: ET.Element) -> int:
        """
        Finds the amount of staves in a <part> element
        :param part_elem:
        :return:
        """
        # Staff count from an <attributes> element
        for measure_elem in part_elem.findall('measure'):
            if (attr_elem := measure_elem.find('attributes')) is not None:
                if attr_elem.find('staves') is not None:
                    return int(attr_elem.find('staves').text)

        # Staff count from notes
        highest_staff = 1
        for measure_elem in part_elem.findall('measure'):
            for note_elem in measure_elem.findall('note'):
                if note_elem.find('staff') is not None:
                    if int(note_elem.find('staff').text) > highest_staff:
                        highest_staff = int(note_elem.find('staff').text)

        return highest_staff

    @classmethod
    def get_attr_staff(cls, attr_elem: ET.Element) -> int:
        """
        Determines which staff an attribute element applies to. Note (in the beginning of the file, unspecified
        attributes may apply to all staves)
        :param attr_elem:
        :return:
        """
        pass

    @classmethod
    def _load_part(cls, part_item: ET.Element, loaded_part: Part) -> Part:
        staff_count: int = MusicXML._get_staff_count(part_item)

        print(f'\nStaff Count: {staff_count}\n')

        # Keeps a running count for time, key, and divs are lists for every staff in the part
        prev_measure: list[Measure | None] = [Measure.empty_measure() for x in range(0, staff_count)]

        measure_marks: list[list[MeasureMark] | None] = [[] for x in range(0, staff_count)]  # [[]] * staff_count

        if 'id' in part_item.attrib.keys():
            loaded_part.id = part_item.get('id')
        else:
            warnings.warn(f'Part has no ID in musicxml file', stacklevel=2)

        # Establishes the initial divisions value -- currently the same one value is used for the entire staff system
        for staff in range(staff_count):
            if part_item.find('measure').find('attributes').find('divisions') is not None:
                prev_measure[staff].divisions = \
                    int(part_item.find('measure').find('attributes').find('divisions').text)
            else:
                raise ImportError('No initial divisions value found')

        current_measure = 0
        for measure_elem in part_item:
            if measure_elem.tag != 'measure':
                raise NotImplementedError(f'The non-measure element {measure_elem.tag} is under the Parts element')

            # For every staff
            # Staff must be incremented sometimes because mxml begins staff index at 1, not 0
            for staff in range(staff_count):

                initial_m = Measure(time=prev_measure[staff].time, key=prev_measure[staff].key,
                                    clef=prev_measure[staff].clef)
                initial_m.transposition = prev_measure[staff].transposition

                # Returns the MEASURE and the running list of MEASURE MARKS
                loaded_measure = MusicXML._load_measure(measure_elem,
                                                        initial_m,
                                                        prev_measure[staff].divisions,
                                                        current_measure,
                                                        measure_marks[staff],
                                                        staff=(staff + 1))
                measure_marks[staff] = loaded_measure[1]

                loaded_part.append(loaded_measure[0], staff + 1)

                # Updates the divisions amount if applicable
                for attribute_element in measure_elem.findall('attributes'):
                    if attribute_element.find('divisions') is not None:
                        prev_measure[staff].divisions = int(attribute_element.find('divisions').text)

                # UPDATE THE RUNNING TIME SIGNATURE OR THE NEW MEASURE
                if loaded_measure[0].time is not None:
                    prev_measure[staff].time = loaded_measure[0].time
                else:
                    loaded_measure[0].time = prev_measure[staff].time

                # UPDATE THE RUNNING KEY OR THE NEW MEASURE
                if loaded_measure[0].key is not None:
                    prev_measure[staff].key = loaded_measure[0].key
                else:
                    loaded_measure[0].key = prev_measure[staff].key

                # UPDATE THE RUNNING CLEF OR THE NEW MEASURE
                if loaded_measure[0].clef is not None:
                    prev_measure[staff].clef = loaded_measure[0].clef
                else:
                    loaded_measure[0].clef = prev_measure[staff].clef

                # UPDATE THE RUNNING TRANSPOSITION OR THE NEW MEASURE
                if loaded_measure[0].transposition is not None:
                    prev_measure[staff].transposition = loaded_measure[0].transposition
                else:

                    if prev_measure[staff].transposition is None:
                        loaded_measure[0].transposition = Transposition()
                    else:
                        loaded_measure[0].transposition = prev_measure[staff].transposition

                # Implement every completed measure mark:
                # TODO: Set this up so it appends to staff-specific measure mark lists
                for mm in measure_marks[staff]:
                    # A non-InstantaneousMeasureMark is completed if it's end_point is not 0
                    if mm is not InstantaneousMeasureMark and mm.end_point != 0:

                        if mm.measure_index < len(loaded_part.measures):
                            print(
                                f'MM starting at {mm.start_point}, ending at '
                                f'{mm.end_point}, with measure_span {mm.measure_span} has been added to measure '
                                f'{mm.measure_index}!')

                            # Append the MeasureMark to the part's measure
                            loaded_part.measures[mm.measure_index].measure_marks.append(mm)
                            # Remove this MeasureMark from the running-total list of measure marks
                            measure_marks.remove(mm)

                # TODO: Set this up so it appends to staff-specific measure mark lists
                # MeasureMarks that have not been resolved yet are noted to span for +1 measure
                for mm in measure_marks:
                    if isinstance(mm, MeasureMark):
                        print(f'incrementing measure span for {mm}')
                        mm.measure_span += 1

                print(f'\nCurrent persisting MeasureMarks: {measure_marks}\n')

            current_measure += 1

        # At the end of the constructed part:
        # Unresolved MeasureMarks are now wrapped up, with their end being at the score-end

        # TODO: Set this up so it appends to staff-specific measure mark lists
        for mm in measure_marks[0]:  # TODO: <- this [0] is a stand-in
            mm.end_point = 0
            loaded_part.measures[mm.measure_index].measure_marks.append(mm)

        return copy.deepcopy(loaded_part)

    @classmethod
    def _load_measure_mark(cls, mark_element: ET.Element) -> MeasureMark:
        pass

    @classmethod
    def _element_is_in_staff(cls, elem: ET.Element, staff: int) -> bool:
        """
        Tells if the passed in element interacts with the specific, passed in staff number. Currently, works for <note>,
         <direction>, <clef>, <time>, and <key> elements
        :param elem: The element to test if it only applies to a certain staff
        :param staff: The staff number, starting from 1 and increasing for every staff
        :return:
        """
        if not isinstance(elem, ET.Element):
            raise TypeError(f'Cannot use {elem} of type {type(elem)} as an element.')

        match elem.tag:

            case 'key' | 'time':
                if elem.get('number') is None:
                    return True
                else:
                    return int(elem.get('number')) == staff

            case 'clef':
                if elem.get('number') is None:
                    return staff == 1
                else:
                    return int(elem.get('number')) == staff

            case 'note' | 'direction':
                if elem.find('staff') is None:
                    return staff == 1
                else:
                    return int(elem.find('staff').text) == staff

            case _:
                raise ValueError(f'Cannot determine whether {elem} of tag {elem.tag} exists for a specific staff.')

    @classmethod
    def _load_notegroup(cls, first_note: Note | NoteGroup, added_elem: ET.Element, divisions: int) \
            -> (NoteGroup, int):
        """
        This turns the new element into a note and then adds it to the first group, making it a notegroup. This
         new notegroup is then returned, along with the change in musical location.

        :param first_note:
        :param added_elem:
        :return: New note group and the change in musical location
        """

        # Make sure there's a notegroup
        if not isinstance(first_note, NoteGroup):
            first_note = NoteGroup.from_note(first_note)

        new_note_info = MusicXML._load_note(added_elem, divisions)
        first_note.append_note(new_note_info[0])

        return first_note, new_note_info[1]

    @classmethod
    def _load_measure(cls,
                      measure_element: ET.Element,
                      measure: Measure,
                      divisions: int,
                      measure_index: int,
                      measure_marks: list[MeasureMark],
                      staff: int = 1) -> (Measure, list[MeasureMark]):
        """
        Loads a measure element from a partwise musicxml file

        :param measure_element: The musicxml measure element to be loaded
        :param measure: The measure which describes what key and clef the measure will take place in
        :param divisions: Divisions per quarter note, used to compute the note's value
        :param measure_index: Dictates what index this measure will be in the part list it's appended to
        :param measure_marks: List used to keep a running total of to-be-inserted measure marks
        :param staff: Dynamically searches for staff-specific elements based on the staff number that is passed in
        :return: The measure described by the xml file and an updated list of MeasureMarks
        """
        print(f'=====Measure {measure_index}, staves:{staff}=====')

        current_musical_location = 0  # incremented as more notes are added

        n = 1
        for item in measure_element:

            print(f'--{n}: Reading {item.tag} at location {current_musical_location}')
            n += 1

            match item.tag:

                case 'attributes':
                    for child in item:
                        match child.tag:
                            case 'clef':

                                if not MusicXML._element_is_in_staff(child, staff):
                                    continue

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
                                print(f'NEW CLEF HAS BEEN UPDATED: {measure.clef}')

                            case 'divisions':
                                divisions = int(child.text)

                            case 'key':
                                if not MusicXML._element_is_in_staff(child, staff):
                                    continue

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
                                pass

                            case 'time':
                                if not MusicXML._element_is_in_staff(child, staff):
                                    continue

                                measure.display_time = True
                                new_time_signature = TimeSignature()

                                # Beats and beat type
                                for time_item in child:
                                    if time_item.tag == 'beats':
                                        new_time_signature.numerator = int(time_item.text)
                                    elif time_item.tag == 'beat-type':
                                        new_time_signature.denominator = int(time_item.text)
                                    else:
                                        print(f'{time_item.tag} is not supported yet')

                                # Time symbol type
                                new_time_signature.timesymboltype = XMLConversion.time_symbol_type_from_mxml(child)

                                measure.time = new_time_signature

                            case 'transpose':
                                # TODO: If there is no "number" attrib, this applies to all staves in the part...

                                if measure.transposition is None:
                                    measure.transposition = Transposition()

                                for tr_child in child:

                                    if tr_child.tag == 'diatonic':
                                        measure.transposition.diatonic = int(tr_child.text)

                                    elif tr_child.tag == 'chromatic':
                                        measure.transposition.chromatic = int(tr_child.text)

                                    elif tr_child.tag == 'octave-change':
                                        measure.transposition.octave_change = int(tr_child.text)

                                    elif tr_child.tag == 'double':
                                        measure.transposition.doubled = True

                            case 'measure_style':
                                print(f'Measure Style not supported yet')

                            case _:
                                print(f'{child.tag.title()} under "Measure" is not supported yet')

                case 'note':

                    # If this note is not a part of the current staff, skip it
                    if not MusicXML._element_is_in_staff(item, staff):
                        continue
                    if measure.time is None or measure.key is None:
                        raise ValueError(f'Time and key should already be set--logically need to set them up.')

                    # IS IN PREVIOUS CHORD
                    if item.find('chord') is not None:

                        # Make a new note group using the latest note
                        new_note_group = MusicXML._load_notegroup(measure.notes[-1], item, divisions)

                        measure.notes[-1] = new_note_group[0]  # New note group
                        current_musical_location += new_note_group[1]  # Change in location

                    # IS NOT IN PREVIOUS CHORD
                    else:
                        loaded_note = MusicXML._load_note(item, divisions)

                        measure.append(loaded_note[0])  # New note
                        current_musical_location += loaded_note[1]  # Change in location

                case 'backup':
                    pass
                    # print(f'{item.tag.title()} in Measure has not been implemented yet')

                case 'forward':
                    pass

                case 'direction':

                    if not MusicXML._element_is_in_staff(item, staff):
                        continue

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
                    measure.barline = XMLConversion.barline_from_mxml(item)

                case 'grouping':
                    pass
                case 'link':
                    pass
                case 'bookmark':
                    pass

                case _:
                    raise NotImplementedError(f'Measure for {item.tag}')

        print(f'This measure has stemtypes: {[n.stem for n in measure.notes]}')
        return copy.deepcopy(measure), measure_marks

    @classmethod
    def _load_note(cls, note_item: ET.Element, divisions: int) -> (Note, int, int):
        """
        Returns a note described by the musicxml file and how far the measure has proceeded

        :param note_item: Note element from the musicxml file
        :param divisions: Divisions per quarter note, used to compute the note's value
        :return: The note described by the musicxml file, an integer describing how far the measure has
        proceeded, in relation to the divisions, and which staff this should be applied to
        """
        # Deep copy needs to be called for some reason? Otherwise, note attributes persist when Note() is called again
        note = copy.deepcopy(Note())
        duration = 0
        staff = 1

        # Dots and ratio are pre-set to find the notevalue more easily:
        note.value.dots = len(note_item.findall('dot'))
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
                    pass  # Accounted for in the next if-statement

                else:
                    warnings.warn(f'Time element {time_mod_item.tag.title()} not implemented.',
                                  stacklevel=2)

            # If there are dots elements in time-modification, it should equal note.value.dots
            if (tm_dots := len(tm.findall('normal-dot'))) is not None:
                if tm_dots != note.value.dots.value:
                    warnings.warn('Inconsistent dot values in musicxml file: count of <dots> is not equal'
                                  ' to count of <normal-dot>.', stacklevel=2)

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
                    for pitch_item in note_child:

                        note.is_pitched = False

                        if pitch_item.tag == 'display-octave':
                            note.pitch.octave = Octave.from_int(int(pitch_item.text))

                        elif pitch_item.tag == 'display-step':
                            note.pitch.step = Step[pitch_item.text]

                        else:
                            raise NotImplementedError(f'Pitch for {pitch_item.tag}')

                case 'rest':
                    note = Rest.to_rest(note)

                case 'tie':
                    # Tie so far is accounted for in <notations>
                    # print(f'"{note_child.tag.title()}" note element has not been implemented yet.')
                    pass

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
                    note.stem = XMLConversion.stemtype_from_mxml(note_child)

                case 'notehead':
                    note.notehead = XMLConversion.notehead_from_mxml(note_child)

                case 'notehead-text':
                    pass

                case 'staff':
                    staff = int(note_child.text)

                case 'beam':
                    if (new_beam := XMLConversion.beam_from_mxml(note_child)) is not None:
                        note.add_beam(new_beam)

                case 'notations':

                    for notation in note_child:

                        if notation.tag == 'tied' or notation.tag == 'slur':
                            note.add_notemark(XMLConversion.note_mark_from_mxml(notation))

                        elif notation.tag == 'articulations':
                            for articulation in notation:
                                note.add_notemark(XMLConversion.note_mark_from_mxml(articulation))

                        elif notation.tag == 'ornaments':
                            for ornament in notation:
                                note.add_notemark(XMLConversion.note_mark_from_mxml(ornament))

                        else:
                            pass

                case 'lyric':
                    note.lyric = XMLConversion.lyric_from_mxml(note_child)

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
            #
            # elif note_child.tag == 'staff':
            #     staff = int(note_child.text)
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
            # elif note_child.tag == 'voice':
            #     voice = int(note_child.text)
            # else:
            #     raise ValueError('note for {0}'.format(note_child.tag))

        # print(duration, time.divisions, time.denominator)
        # notetype, nt_exact = NoteType.find(duration / time.divisions / time.denominator)
        # print('notetype', notetype, notetype.duration, (duration / time.divisions / time.denominator), nt_exact)
        # print('tuplet', Tuplet.find(duration / time.divisions / time.denominator))

        # if pitch is not None:
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

        # Need to use copy.deepcopy so that using _load_note again won't affect past notes
        return copy.deepcopy(note), duration, staff

    @staticmethod
    def load(xml_file: str) -> Score:
        """
        Loads a MusicXML file and converts to a Score.


        """

        # process xml root
        # create element tree object
        tree = ET.parse(xml_file)

        # get root element
        root = tree.getroot()

        loaded_score = Score()
        if root.tag == 'score-partwise':
            loaded_score = MusicXML._load_partwise(root)
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

    # NEW IDEA FOR SAVE MEASURE ATTRIBUTES: take in the ENTIRE PART and then an INTEGER that describes the MEASURE INDEX
    # Then COMPARE every measure based off of its PRECEEDING ONE

    @classmethod
    def _save_measure_attributes(cls,
                                 part: Part,
                                 m_index: int) -> ET.Element | None:
        """
        Based on the passed in measure index, reviews the indexed measure for every single staff in the part and then
        constructs an attribute element based off of that

        :param part: The part being accessed with the measure index
        :param m_index: The index of the saved measure: index of the measure this attribute element is based on
        :return: A measure's attribute element
        """
        # Will be used if there is a new key, clef, or time signature
        attributes_elem = None

        # NOW: compare each measure's notation to the previous measure's notation--if not equivilant, then notate this
        # new notation

        # NEW DIVISION OF NOTES
        if m_index == 0 or part.measures[m_index].divisions is not part.measures[m_index - 1].divisions:
            attributes_elem = ET.Element('attributes')

            ET.SubElement(attributes_elem, 'divisions')
            attributes_elem.find('divisions').text = str(int(part.measures[m_index].divisions))

        # NEW KEY (Traditional Style)
        if m_index == 0 or not part.measures[m_index].key.is_equivilant(part.measures[m_index - 1].key):

            # Make the 'attributes' elem if it hasn't been made yet
            if attributes_elem is None:
                attributes_elem = ET.Element('attributes')

            key_elem = ET.SubElement(attributes_elem, 'key')
            ET.SubElement(key_elem, 'fifths')
            key_elem.find('fifths').text = str(part.measures[m_index].key.fifths())
            ET.SubElement(key_elem, 'mode')
            key_elem.find('mode').text = part.measures[m_index].key.modetype_to_str()

        # NEW TIME SIGNATURE
        if m_index == 0 or not part.measures[m_index].time.is_equivilant(part.measures[m_index - 1].time):

            if attributes_elem is None:
                attributes_elem = ET.Element('attributes')

            time_elem = ET.SubElement(attributes_elem, 'time')

            # Symbol
            time_elem.attrib['symbol'] = XMLConversion.time_symbol_type_to_mxml(part.measures[m_index].time)

            # Beats and beat type
            ET.SubElement(time_elem, 'beats')
            time_elem.find('beats').text = str(part.measures[m_index].time.numerator)
            ET.SubElement(time_elem, 'beat-type')
            time_elem.find('beat-type').text = str(part.measures[m_index].time.denominator)

        # STAVES
        if m_index == 0:
            if attributes_elem is None:
                attributes_elem = ET.Element('attributes')

            ET.SubElement(attributes_elem, 'staves')
            attributes_elem.find('staves').text = str(part.staff_count())

        # NEW PRIMARY-STAFF CLEF
        if m_index == 0 or not part.measures[m_index].clef.is_equivilant(part.measures[m_index - 1].clef):

            if attributes_elem is None:
                attributes_elem = ET.Element('attributes')

            attributes_elem.append(XMLConversion.clef_to_mxml(part.measures[m_index].clef, clef_number=1))

        # NEW SECONDARY-STAFF CLEFS
        for staff in range(part.staff_count() - 1):

            # Gets the new and old clef for comparing
            old_st_clef = None
            if m_index != 0:
                old_st_clef = copy.deepcopy(part.multi_staves[staff][m_index - 1].clef)
            new_st_clef = copy.deepcopy(part.multi_staves[staff][m_index]).clef

            # If new clef is unequal to previous:
            if m_index == 0 or not new_st_clef.is_equivilant(old_st_clef):

                if attributes_elem is None:
                    attributes_elem = ET.Element('attributes')

                attributes_elem.append(XMLConversion.clef_to_mxml(new_st_clef, clef_number=staff + 2))

        # NEW PRIMARY_STAFF TRANSPOSE
        first_irregular_trans = m_index == 0 and not part.measures[m_index].transposition.is_equivilant(Transposition())
        if first_irregular_trans or \
                (m_index != 0 and
                 not part.measures[m_index].transposition.is_equivilant(part.measures[m_index - 1].transposition)):

            if attributes_elem is None:
                attributes_elem = ET.Element('attributes')

            trans_elem = ET.SubElement(attributes_elem, 'transpose', {'number': '1'})

            ET.SubElement(trans_elem, 'diatonic')
            trans_elem.find('diatonic').text = str(part.measures[m_index].transposition.diatonic)
            ET.SubElement(trans_elem, 'chromatic')
            trans_elem.find('chromatic').text = str(part.measures[m_index].transposition.chromatic)
            ET.SubElement(trans_elem, 'octave-change')
            trans_elem.find('octave-change').text = str(part.measures[m_index].transposition.octave_change)

            if part.measures[m_index].transposition.doubled:
                ET.SubElement(trans_elem, 'double')

        # NEW SECONDARY_STAFF TRANSPOSE
        for staff in range(part.staff_count() - 1):

            # Gets the new and old tranposition for comparing
            old_transpose = Transposition()
            if m_index != 0:
                old_transpose = copy.deepcopy(part.multi_staves[staff][m_index - 1].transposition)
            new_tranpose = copy.deepcopy(part.multi_staves[staff][m_index]).transposition

            # If new tranposition is unequal to previous:
            first_irregular_trans = m_index == 0 and not new_tranpose.is_equivilant(Transposition())
            if first_irregular_trans or (m_index != 0 and not new_tranpose.is_equivilant(old_transpose)):

                if attributes_elem is None:
                    attributes_elem = ET.Element('attributes')

                trans_elem = ET.SubElement(attributes_elem, 'transpose', {'number': f'{staff + 2}'})

                ET.SubElement(trans_elem, 'diatonic')
                trans_elem.find('diatonic').text = str(new_tranpose.diatonic)
                ET.SubElement(trans_elem, 'chromatic')
                trans_elem.find('chromatic').text = str(new_tranpose.chromatic)
                ET.SubElement(trans_elem, 'octave-change')
                trans_elem.find('octave-change').text = str(new_tranpose.octave_change)

                if new_tranpose.doubled:
                    ET.SubElement(trans_elem, 'double')

        return attributes_elem

    @classmethod
    def _sort_note_notations(cls, notat_elem: ET.Element) -> ET.Element:
        """
        The children of the <notations> element must follow a specific order. This takes in a <notations> element
        and returns the properly sorted one

        :param notat_elem:
        :return:
        """
        # Makes a sorted list of <notation>'s children
        new_notat_order = sorted([child for child in notat_elem], key=XMLConversion.notations_order_key)

        # Replaces each child with the sorted one
        for i in range(len([child for child in notat_elem])):
            notat_elem[i] = new_notat_order[i]

        return notat_elem

    @classmethod
    def _save_note_notations(cls, saved_note: Note) -> ET.Element:
        notat_elem = ET.Element('notations')

        for nm in saved_note.marks:

            # Tied
            if isinstance(nm, TieType):
                ET.SubElement(notat_elem, 'tied')
                notat_elem.find('tied').attrib['type'] = nm.name.lower()

            # Slur
            if isinstance(nm, SlurType):
                ET.SubElement(notat_elem, 'slur')
                notat_elem.find('slur').attrib['type'] = nm.name.lower()

            # Articulation
            if isinstance(nm, ArticulationType):
                if notat_elem.find('articulations') is None:
                    ET.SubElement(notat_elem, 'articulations')

                match nm:
                    case ArticulationType.ACCENT:
                        ET.SubElement(notat_elem.find('articulations'), 'accent')
                    case ArticulationType.STACCATO:
                        ET.SubElement(notat_elem.find('articulations'), 'staccato')
                    case _:
                        pass

            # Ornamen
            elif isinstance(nm, OrnamentType):
                if notat_elem.find('ornaments') is None:
                    ET.SubElement(notat_elem, 'ornaments')

                match nm:
                    case OrnamentType.TURN:
                        ET.SubElement(notat_elem.find('ornaments'), 'turn')
                    case _:
                        pass

            else:
                pass

        # Must sort the order of <notations>'s children, otherwise <notations> isn't viable
        if len([child for child in notat_elem]) > 1:
            notat_elem = MusicXML._sort_note_notations(notat_elem)

        return notat_elem

    @classmethod
    def _save_note(cls, saved_note: Note, staff: int = 1, voice: int = 1) -> ET.Element:
        """
        Creates a note mxml element based on a MusicAI note and staff line. Staff lines start at 1, and increase for
        every secondary staff. <voice> does not have complete functionality yet.

        :param saved_note:
        :param staff: Represents which staff the note starts one, and starts at 1
        :return:
        """
        note_elem = ET.Element('note', {'color': '#000000'})

        # REST
        if saved_note.is_rest():
            ET.SubElement(note_elem, 'rest')

        # PITCH
        elif saved_note.is_pitched:
            pitch_elem = ET.SubElement(note_elem, 'pitch')

            ET.SubElement(pitch_elem, 'step')
            pitch_elem.find('step').text = str(saved_note.pitch.step)

            from musicai.structure.pitch import Accidental
            if saved_note.pitch.alter != Accidental.NONE:
                # TODO: Implement accidental.to_mxml() (not high priority)
                ET.SubElement(pitch_elem, 'alter')
                if float(saved_note.pitch.alter).is_integer():
                    note_alter = int(float(saved_note.pitch.alter))
                else:
                    note_alter = float(saved_note.pitch.alter)
                pitch_elem.find('alter').text = str(note_alter)

            ET.SubElement(pitch_elem, 'octave')
            pitch_elem.find('octave').text = str(int(saved_note.pitch.octave))

        # UNPITCHED
        else:
            unpitched_elem = ET.SubElement(note_elem, 'unpitched')

            ET.SubElement(unpitched_elem, 'display-step')
            unpitched_elem.find('display-step').text = str(saved_note.pitch.step)

            ET.SubElement(unpitched_elem, 'display-octave')
            unpitched_elem.find('display-octave').text = str(int(saved_note.pitch.octave))

        # DURATION
        ET.SubElement(note_elem, 'duration')

        # Calculates it and converts to int form if possible
        duration_value = (saved_note.value.value * 4) * saved_note.division * \
                         saved_note.value.ratio.normal / saved_note.value.ratio.actual  # saved_note.value.dots * \

        if duration_value.is_integer():
            duration_value = int(duration_value)

        note_elem.find('duration').text = str(duration_value)

        # TIE
        for nm in saved_note.marks:
            if isinstance(nm, TieType):
                new_tie = ET.SubElement(note_elem, 'tie')
                new_tie.attrib['type'] = nm.name.lower()

        # VOICE
        ET.SubElement(note_elem, 'voice')
        voice_rep = voice + (staff - 1)
        note_elem.find('voice').text = f'{voice_rep}'

        # TYPE
        if (type_text := XMLConversion.notetype_to_mxml(saved_note)) != '':
            ET.SubElement(note_elem, 'type')
            note_elem.find('type').text = type_text

        # DOTS
        if saved_note.get_dot_count() != 0:
            for n in range(saved_note.get_dot_count()):
                ET.SubElement(note_elem, 'dot')

        # TIME MODIFICATION
        if not saved_note.value.ratio.is_regular():
            note_elem.append(XMLConversion.ratio_to_mxml(saved_note))

        # STEM
        if not saved_note.is_rest():
            note_elem.append(XMLConversion.stemtype_to_mxml(saved_note.stem))

        # NOTEHEAD
        if not saved_note.has_normal_notehead():
            note_elem.append(XMLConversion.notehead_to_mxml(saved_note.notehead))

        # STAFF
        ET.SubElement(note_elem, 'staff')
        note_elem.find('staff').text = f'{staff}'

        # BEAM
        for beam in saved_note.beams:
            note_elem.append(XMLConversion.beam_to_mxml(beam))

        # NOTATIONS
        if len(saved_note.marks) != 0:
            # Create the <notations> element to include all note marks
            note_elem.append(MusicXML._save_note_notations(saved_note))

        # LYRIC
        if saved_note.lyric is not None:
            note_elem.append(XMLConversion.lyric_to_mxml(saved_note.lyric))

        return note_elem

    @classmethod
    def _save_note_group(cls, saved_note: NoteGroup, staff: int = 1, voice: int = 1) -> list[ET.Element]:
        """
        Creates a list of note elements that have the <chord> element, which collectively form a chord

        :param saved_note:
        :param staff:
        :param voice:
        :return:
        """

        note_elems: list[ET.Element] = []

        # Makes an element for every note
        for note in saved_note.notes:
            note_elems.append(MusicXML._save_note(note, staff, voice))

        # Adds the chord elements
        for i in range(len(note_elems)):

            # Don't add <chord> to the first note element
            if i == 0:
                continue

            # The <chord> element is only preceeded by <cue> and <grace> elements
            ch_index: int = 0
            ch_index += len(note_elems[i].findall('cue')) + len(note_elems[i].findall('grace'))

            note_elems[i].insert(ch_index, ET.Element('chord'))

        return note_elems

    @classmethod
    def _save_part(cls, part_elem: ET.Element, saved_part: Part, part_count: int) -> ET.Element:
        """
        Currently does not support overlapping measure marks yet

        :param part_elem:
        :param saved_part:
        :param part_count:
        :return:
        """

        # Keeps a running total of measure marks
        s_measure_marks_to_end = []

        # FOR EVERY MEASURE
        measure_index = 0
        for measure in saved_part.measures:

            # Add the beginning divider
            measure_divider = ET.Comment(f'============== Part: P{part_count}, Measure: {measure_index + 1}'
                                         f' ==============')
            part_elem.append(measure_divider)

            new_measure_elem = ET.SubElement(part_elem, 'measure', {'number': f'{measure_index + 1}'})

            # Updates the attributes element
            attribute_elem = MusicXML._save_measure_attributes(saved_part, measure_index)
            if attribute_elem is not None:
                new_measure_elem.append(attribute_elem)

            # LEFT-SIDED BARLINE
            if measure.has_ls_barline():
                warnings.warn(f'Measure {measure} has a left-sided barline that HAS NOT been represented!')

            # NOTES and MEASURE MARKS
            current_musical_pos = 0
            measure_marks_to_save = measure.measure_marks.copy()

            # FOR EVERY NOTE
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
                                          {'color': '#000000', 'type': MusicXML.measure_mark_mxml_type(mm)})

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

                # NOTE GROUP
                if isinstance(s_note, NoteGroup):
                    for elem in MusicXML._save_note_group(s_note, 1):
                        new_measure_elem.append(elem)

                # NOTE
                else:
                    new_measure_elem.append(MusicXML._save_note(s_note, 1))

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

            # FOR EVERY NOTE IN THE MULTI STAVES
            for staff in range(saved_part.staff_count() - 1):

                # First, add the backup element
                backup_count = (measure.divisions * 4) * measure.time.numerator / measure.time.denominator
                if backup_count.is_integer():
                    backup_count = int(backup_count)
                ET.SubElement(new_measure_elem, 'backup')
                ET.SubElement(new_measure_elem.find('backup'), 'duration')
                new_measure_elem.find('backup').find('duration').text = str(backup_count)

                # Next, add every note
                for s_note in saved_part.multi_staves[staff][measure_index].notes:

                    # NOTE GROUP
                    if isinstance(s_note, NoteGroup):
                        for elem in MusicXML._save_note_group(s_note, staff + 2):
                            new_measure_elem.append(elem)

                    # NOTE
                    else:
                        new_measure_elem.append(MusicXML._save_note(s_note, staff + 2))

            # IRREGULAR RS BARLINE
            if measure.has_irregular_rs_barline():

                bl_elem = XMLConversion.barline_to_mxml(measure.barline)
                new_measure_elem.append(bl_elem)

            # REGULAR RS BARLINE
            else:
                right_barline = ET.SubElement(new_measure_elem, 'barline', {'location': 'right'})
                ET.SubElement(right_barline, 'bar-style')
                right_barline.find('bar-style').text = 'regular'

            # Update measure index
            measure_index += 1

        return part_elem

    @staticmethod
    def save(score: Score, xml_file: str):
        """
        Saves every partsystem, part, measure, and note into the <part-list> and <part> mxml elements.

        Currently, only one tempo is supported in the Score class. This tempo is appended to the tree at the end of
        this function. Only places one tempo at the top of the file.

        :param score:
        :param xml_file:
        :return:
        """
        mxml_body = '<score-partwise version="4.0"><part-list></part-list>' \
                    '</score-partwise>'

        root = ET.fromstring(mxml_body)

        partlist = root.find('part-list')

        # For each part in the score, saves its information
        part_id_num = 1
        for part_system in score.systems:

            # MULTI-PART GROUPING START
            if len(part_system.parts) > 1:
                part_group_elem = ET.SubElement(partlist, 'part-group', {'type': 'start'})

                # Grouping symbol for partsystem
                if str(part_system.grouping_symbol) != '':
                    ET.SubElement(part_group_elem, 'group-symbol')
                    part_group_elem.find('group-symbol').text = \
                        XMLConversion.grouping_symbol_to_mxml(part_system.grouping_symbol)

            # ADD MEASURE INFO
            for part in part_system.parts:

                # MULTI-STAFF GROUPING START
                if part.has_multiple_staves():
                    partgroup = ET.SubElement(partlist, 'part-group', {'type': 'start'})

                    # Grouping symbol for part
                    if str(part.grouping_symbol) != '':
                        ET.SubElement(partgroup, 'group-symbol')
                        partgroup.find('group-symbol').text = \
                            XMLConversion.grouping_symbol_to_mxml(part.grouping_symbol)

                # SAVE PARTLIST METADATA
                score_part_elem = ET.SubElement(partlist, 'score-part')
                score_part_elem = MusicXML._save_part_metadata(score_part_elem, part, part_id_num)

                # MULTI-STAFF GROUPING STOP
                if part.has_multiple_staves():
                    ET.SubElement(partlist, 'part-group', {'type': 'stop'})

                # SAVE EVERY MEASURE
                part_elem = ET.SubElement(root, 'part', {'id': f'P{part_id_num}'})
                part_elem = MusicXML._save_part(part_elem, part, part_id_num)

                # Part ID number is incremented
                part_id_num += 1

            # MULTI-PART GROUPING END
            if len(part_system.parts) > 1:
                ET.SubElement(partlist, 'part-group', {'type': 'stop'})

        # Adds the first tempo marking to top =====================================
        # TODO: Construct vertical beatmap and remove this code
        first_measure = root.find('part').find('measure')
        index = [child for child in first_measure].index(first_measure.find('attributes')) + 1

        dir_elem = ET.Element('direction')
        dirtype_elem = ET.SubElement(dir_elem, 'direction-type')
        metronome = ET.SubElement(dirtype_elem, 'metronome')
        ET.SubElement(metronome, 'beat-unit')
        metronome.find('beat-unit').text = XMLConversion.notetype_to_mxml(score.tempo.beat_unit)
        ET.SubElement(metronome, 'per-minute')
        metronome.find('per-minute').text = str(score.tempo.tempo)

        first_measure.insert(index, dir_elem)
        # ========================================================================

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
    # file = '../../examples/mxml/HelloWorld3.musicxml'
    # file = '../../examples/mxml/io_test/pianotest0.2.musicxml'
    # file = '../../examples/mxml/MahlFaGe4Sample.musicxml'
    # file = '../../examples/mxml/MozaChloSample.musicxml'
    file = '../../examples/mxml/io_test/castaways_fixed.musicxml'
    # file = '../../examples/mxml/MozartPianoSonata.musicxml'
    # file = '../../examples/mxml/MozartTrio.musicxml'
    # file = '../../examples/mxml/MozaVeilSample.musicxml'
    # file = '../../examples/mxml/Saltarello.musicxml'
    # file = '../../examples/mxml/SchbAvMaSample.musicxml'
    # file = '../../examples/mxml/Telemann.musicxml'

    save_file = '../../examples/mxml/io_test/castaways_save.musicxml'

    # Create a score with a note and dynamic change mark
    score_to_save = MusicXML.load(file)

    # score_to_save.print_in_depth()
    # print(f'{score_to_save}')

    MusicXML.save(score_to_save, save_file)


if __name__ == "__main__":
    main()
