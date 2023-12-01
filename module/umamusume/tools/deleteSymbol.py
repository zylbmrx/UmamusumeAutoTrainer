def character_maketrans(inter_str: str):
    # 去除符号
    tb1_character = r',.!?;:()<>[]""\'\'，。！？；：（）《》【】“”\‘\’○♪☆×∴²◎'
    tb2_character = r'                                           '

    # 创建转换表
    table = str.maketrans(tb1_character, tb2_character)
    return inter_str.translate(table).replace(' ', '')


