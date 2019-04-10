NUMBERS = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
]


# https://stackoverflow.com/a/28777781/8704691
def arabic2roman(number):
    result = ''
    for arabic, roman in NUMBERS:
        div = number // arabic
        result += roman * div
        number -= arabic * div
        if number <= 0:
            break
    return result


def roman2arabic(number):
    if not number:
        return 0
    if number[0] == 'M':
        return 1000 + roman2arabic(number[1:])
    if 'D' in number:
        values = range(400, 900)
    elif 'C' in number:
        values = range(90, 1000)
    else:
        values = range(90)
    for arabic in values:
        if arabic2roman(arabic) == number:
            return arabic
    raise ValueError
