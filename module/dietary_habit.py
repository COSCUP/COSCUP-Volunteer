class DietaryHabit(object):
    ''' DietaryHabit class '''

    ITEMS = {
        '0.000': u'葷食',
        '0.001': u'葷食但不能吃牛',
        '0.002': u'葷食但不能吃豬',
        '1.000': u'素食',
        '2.000': u'對花生、蠶豆過敏',
        '3.000': u'蔥蒜過敏',
        '4.000': u'海鮮過敏',
    }

    @classmethod
    def valid(cls, items_no):
        ''' valid data '''
        result = []
        for no in cls.ITEMS:
            if no in items_no:
                result.append(no)

        return result
