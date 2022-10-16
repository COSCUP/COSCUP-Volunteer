''' DietaryHabit '''
from enum import Enum, unique


@unique
class DietaryHabitItemsName(Enum):
    ''' DietaryHabitItemsName

    Attributes:

        A000 (str): `葷食`
        A001 (str): `葷食但不能吃牛`
        A002 (str): `葷食但不能吃豬`
        B000 (str): `素食`
        C000 (str): `對花生、蠶豆過敏`
        D000 (str): `蔥蒜過敏`
        E000 (str): `海鮮過敏`

    !!! tip

        The value will as the selection lists be displayed at front.

    '''
    A000 = '葷食'
    A001 = '葷食但不能吃牛'
    A002 = '葷食但不能吃豬'
    B000 = '素食'
    C000 = '對花生、蠶豆過敏'
    D000 = '蔥蒜過敏'
    E000 = '海鮮過敏'


@unique
class DietaryHabitItemsValue(Enum):
    ''' DietaryHabitItemsValue

    Attributes:

        A000 (str): `0.000`
        A001 (str): `0.001`
        A002 (str): `0.002`
        B000 (str): `1.000`
        C000 (str): `2.000`
        D000 (str): `3.000`
        E000 (str): `4.000`

    !!! tip

        The value will as the value be saved into collection.

    '''
    A000 = '0.000'
    A001 = '0.001'
    A002 = '0.002'
    B000 = '1.000'
    C000 = '2.000'
    D000 = '3.000'
    E000 = '4.000'


def valid_dietary_value(items_no: list[str]) -> list[DietaryHabitItemsValue]:
    ''' valid dietary data

    Args:
        items_no (list): List of \
                [DietaryHabitItemsValue][module.dietary_habit.DietaryHabitItemsValue]'s value.

    REturns:
        Return the only valid datas.

    '''
    result: list[DietaryHabitItemsValue] = []
    for num in items_no:
        try:
            result.append(DietaryHabitItemsValue(num))
        except ValueError:
            pass

    return result
