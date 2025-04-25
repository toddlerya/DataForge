#!/usr/bin/env python
# coding: utf-8
# @File    :   calc.py
# @Time    :   2023/11/28 9:57
# @Author  :   guo qun X2590
# @Desc    :   None


from decimal import ROUND_HALF_UP, Decimal

from server.utils.log import logger


@logger.catch
def float_accurate_round(number: float, place: int = 3) -> str:
    """
    精确四舍五入
    Args:
        number: 需要四舍五入处理的数据
        place: (Optional) 可选参数, 需要保留的小数位数, 默认为3位小数

    Returns:
        str
    """
    # 解决科学计数法不支持的问题
    # 将 9.83899192499877e-05 转为 0.000098389919249987703442350550631....
    str_number = f'{number:.200f}'
    _place = '0' if place == 0 else '0.{}'.format('0' * place)
    _cer = Decimal(str_number).quantize(Decimal(_place), rounding=ROUND_HALF_UP)
    cer = '%.{}f'.format(place) % _cer
    return cer


def float_latest_number_place(number: float) -> int:
    """
    判断一个浮点型数字从左往右非零位的位数
    比如0.00014988395703014306, 其非零位的位数为4
    Args:
        number:

    Returns:

    """
    place = 0
    if str(number).startswith('0.0'):
        split_number = str(number).split('0')
        point_index = split_number.index('.')
        for index, ele in enumerate(split_number[point_index + 1:]):
            if ele:
                place = index + 2
                break
    else:
        place = 1
    return place


def float_round_and_format(number: float, number_place: int = 1) -> str:
    """
    对浮点型数据进行精度四舍五入并且格式化为字符串
    Args:
        number:
        number_place:

    Returns:

    """
    # 对于科学计数法进行位数保留
    if '-' in str(number):
        place = int(str(number).split('-')[1])
        # 如果保留的数字个数大于1, 则给其加位数
        if number_place > 1:
            place += number_place - 1
        standardized_number = float_accurate_round(number=number,
                                                   place=place)
    # 其他类型数据保留非零位位小数
    else:
        place = float_latest_number_place(number)
        # 如果保留的数字个数大于1, 则给其加位数
        if number_place > 1:
            place += number_place - 1
        standardized_number = float_accurate_round(number=number,
                                                   place=place)
    return standardized_number


if __name__ == '__main__':
    test_number = 9.83899192499877e-05
    print(test_number)
    print(float_accurate_round(test_number, place=4))
    print(float_accurate_round(125e-2, place=1))
    print(float_accurate_round(2.809837240177863e-05, place=5))
    print(float_accurate_round(0.9995504260415715, place=1))
    print(float_accurate_round(6.405304547658704, place=1))
    print(float_accurate_round(0.00014988395703014306, place=4))
    print(float_latest_number_place(0.0001498839570301430))
    print(float_latest_number_place(0.014988395703014306))
    print(float_latest_number_place(0.14988395703014306))
