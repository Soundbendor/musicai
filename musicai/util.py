import numpy as np
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


class General:
    # -----------
    # Class Methods
    # -----------
    @classmethod
    def find_closest(cls, sorted_list: list[int | float | np.integer | np.inexact],
                     num: int | float | np.integer | np.inexact) \
            -> int | float | np.integer | np.inexact:
        """
        From a sorted list, returns the value closest to the passed in number. Aided by users on Stack Exchange.

        :param sorted_list: A sorted list of integers
        :param num: a number to compare with
        :return:
        """
        from bisect import bisect_left

        position = bisect_left(sorted_list, num)
        if position == 0:
            return sorted_list[0]
        if position == len(sorted_list):
            return sorted_list[-1]

        prev = sorted_list[position - 1]
        nex = sorted_list[position]
        if nex - num < num - prev:
            return nex
        else:
            return prev
