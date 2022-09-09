''' DietaryHabit '''
from enum import Enum, unique


@unique
class DietaryHabitItemsName(Enum):
    ''' DietaryHabitItemsName '''
    A000 = '葷食'
    A001 = '葷食但不能吃牛'
    A002 = '葷食但不能吃豬'
    B000 = '素食'
    C000 = '對花生、蠶豆過敏'
    D000 = '蔥蒜過敏'
    E000 = '海鮮過敏'


@unique
class DietaryHabitItemsValue(Enum):
    ''' DietaryHabitItemsValue '''
    A000 = '0.000'
    A001 = '0.001'
    A002 = '0.002'
    B000 = '1.000'
    C000 = '2.000'
    D000 = '3.000'
    E000 = '4.000'


def valid_dietary_value(items_no: list[str]) -> list[str]:
    ''' valid dietary data

    Args:
        items_no (list): List of \
                [DietaryHabitItemsValue][module.dietary_habit.DietaryHabitItemsValue]'s value.

    REturns:
        Return the only valid datas.

    '''
    result = []
    for num in items_no:
        try:
            DietaryHabitItemsValue(num)
            result.append(num)
        except ValueError:
            pass

    return result


class DietaryHabit:  # pylint: disable=too-few-public-methods
    ''' DietaryHabit class

    Attributes:
        ITEMS (dict): The mapping datas.

            - `0.000`: `葷食`
            - `0.001`: `葷食但不能吃牛`
            - `0.002`: `葷食但不能吃豬`
            - `1.000`: `素食`
            - `2.000`: `對花生、蠶豆過敏`
            - `3.000`: `蔥蒜過敏`
            - `4.000`: `海鮮過敏`

    TODO:
        Need refactor in pydantic.

    '''

    ITEMS = {
        '0.000': '葷食',
        '0.001': '葷食但不能吃牛',
        '0.002': '葷食但不能吃豬',
        '1.000': '素食',
        '2.000': '對花生、蠶豆過敏',
        '3.000': '蔥蒜過敏',
        '4.000': '海鮮過敏',
    }

    @classmethod
    def valid(cls, items_no: list[str]) -> list[str]:
        ''' valid data

        Args:
            items_no (list): List of `ITEMS`'s key.

        REturns:
            Return the only valid datas.

        '''
        result = []
        for num in cls.ITEMS:
            if num in items_no:
                result.append(num)

        return result
