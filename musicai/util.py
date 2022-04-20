from typing import Union
import enum
from enum import Enum
import warnings


class EnumChecker:
    # -----------
    # Class Methods
    # -----------
    @staticmethod
    def find_enum(target_enum: enum.EnumMeta, value: Union[str, Enum, None]) -> Union[Enum, None]:
        """
            Returns the value as an enumeration member if it's the name of an enumeration or already an enumeration
            member.

            :param target_enum: The enumeration that the member is tested to belong to
            :param value: Represents an enumeration member or string of the member's name
        """
        if isinstance(value, str):
            if value.upper() in [e.name for e in target_enum]:
                return target_enum[value.upper()]
            elif value == '':
                if 'NONE' in [e.name for e in target_enum]:
                    return target_enum['NONE']
            else:
                raise ValueError(f'\'{value}\' is not a valid member of {target_enum.__name__}.')

        elif issubclass(type(value), target_enum):
            return value

        elif value is None:
            if 'NONE' in [e.name for e in target_enum]:
                return target_enum['NONE']
            else:
                raise ValueError(f'\'{value}\' is not a valid member of {target_enum.__name__}.')

        else:
            warnings.warn(f'Cannot make {target_enum.__name__} from {value} of type {type(value)}.',
                          stacklevel=2)
            return None
