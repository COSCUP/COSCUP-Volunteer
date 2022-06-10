''' DietaryHabit '''


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
