import datetime
import random

from faker.providers import BaseProvider


# 假设这是你的身份证生成算法 (你需要替换成你自己的真实算法)
def generate_chinese_id_card_number(birth_date=None, province_code=None, gender=None):
    """
    这是一个非常简化的身份证生成器示例，不保证完全符合校验规则或真实性。
    你需要用你自己的真实算法替换它。
    """
    if province_code:
        province_code_str = str(province_code)
        if len(province_code_str) == 2:
            # 补充4位随机数生成完整的6位行政区划代码
            region_prefix = province_code_str + "".join(
                str(random.randint(0, 9)) for _ in range(4)
            )
        elif len(province_code_str) == 4:
            # 补充2位随机数
            region_prefix = province_code_str + "".join(
                str(random.randint(0, 9)) for _ in range(2)
            )
        elif len(province_code_str) == 6:
            region_prefix = province_code_str
        else:
            raise ValueError("province_code must be 2, 4, or 6 digits")
    else:
        # 简化：随机选择一个常见的地区码前缀
        common_prefixes = [
            "1101",
            "3101",
            "4401",
            "5101",
            "3201",
        ]  # 北京、上海、广州、成都、南京等
        # 随机选择一个常见前缀并补充2位随机数
        region_prefix = random.choice(common_prefixes) + "".join(
            str(random.randint(0, 9)) for _ in range(2)
        )

    if birth_date:
        if isinstance(birth_date, str):
            birth_date_obj = datetime.datetime.strptime(birth_date, "%Y%m%d").date()
        elif isinstance(birth_date, datetime.date):
            birth_date_obj = birth_date
        else:
            raise ValueError(
                "birth_date must be a string 'YYYYMMDD' or a datetime.date object"
            )
    else:
        # 随机生成一个生日 (18-60岁)
        start_date = datetime.date(datetime.date.today().year - 100, 1, 1)
        end_date = datetime.date(datetime.date.today().year - 1, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        birth_date_obj = start_date + datetime.timedelta(days=random_number_of_days)

    birth_date_str = birth_date_obj.strftime("%Y%m%d")

    # 顺序码，后三位，倒数第二位是性别 (奇男偶女)
    seq = random.randint(10, 99)  # 前两位随机
    if gender is not None:  # 0 for female, 1 for male
        sex_digit = (
            random.choice([0, 2, 4, 6, 8])
            if gender == 0
            else random.choice([1, 3, 5, 7, 9])
        )
    else:
        sex_digit = random.randint(0, 9)

    sequence_code = f"{seq:02d}{sex_digit}"

    # 校验码 (这里用随机数代替，真实算法需要计算)
    # 真实算法: (∑(Ai * Wi)) mod 11 -> 查表得校验码
    # Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码表: 0->1, 1->0, 2->X, 3->9, 4->8, 5->7, 6->6, 7->5, 8->4, 9->3, 10->2
    body = region_prefix + birth_date_str + sequence_code

    # 简化校验码
    # check_digit = str(random.randint(0,9)) # 真实情况不能这样

    # 稍微真实一点的校验码计算 (不完整，但比随机好)
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_map = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]
    s = sum(int(body[i]) * weights[i] for i in range(17))
    check_digit = check_map[s % 11]

    return body + check_digit


class ChineseIdCardProvider(BaseProvider):
    def id_card_number(self, birth_date=None, province_code=None, gender=None):
        """
        生成一个（伪）真实的中国身份证号码。
        :param birth_date: datetime.date 对象或 "YYYYMMDD" 格式字符串
        :param province_code: 省份行政区划代码前两位或前四位 (e.g., 11, 1101)
        :param gender: 0 for female, 1 for male
        """
        # 调用你实际的身份证生成算法
        return generate_chinese_id_card_number(birth_date, province_code, gender)


# --- 接续主程序 ---
if __name__ == "__main__":
    # ... (上面的 ChineseAddressProvider 和 create_sample_db 代码) ...

    from faker import Faker

    # 1. 创建示例数据库 (实际使用时你的数据库已存在)
    # create_sample_db() # 假设已创建或不需要
    # 2. 初始化 Faker 实例
    fake = Faker("zh_CN")

    # 3. 添加自定义 Provider
    fake.add_provider(ChineseIdCardProvider)

    # 4. 使用自定义 Provider 生成数据
    print("\n--- 身份证信息 ---")
    print(f"随机身份证: {fake.id_card_number()}")
    print(
        f"男性，生日19920608, 曲阜地区: {fake.id_card_number(birth_date='19010608', province_code='370881', gender=1)}"
    )
    from datetime import date

    print(
        f"女性，生日19851225: {fake.id_card_number(birth_date=date(1985,12,25), gender=0)}"
    )
    print("-" * 20)
