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
            "1201",
            "1301",
            "1302",
            "1303",
            "1304",
            "1305",
            "1306",
            "1307",
            "1308",
            "1309",
            "1310",
            "1311",
            "1390",
            "1401",
            "1402",
            "1403",
            "1404",
            "1405",
            "1406",
            "1407",
            "1408",
            "1409",
            "1410",
            "1411",
            "1501",
            "1502",
            "1503",
            "1504",
            "1505",
            "1506",
            "1507",
            "1508",
            "1509",
            "1522",
            "1525",
            "1529",
            "2101",
            "2102",
            "2103",
            "2104",
            "2105",
            "2106",
            "2107",
            "2108",
            "2109",
            "2110",
            "2111",
            "2112",
            "2113",
            "2114",
            "2201",
            "2202",
            "2203",
            "2204",
            "2205",
            "2206",
            "2207",
            "2208",
            "2224",
            "2301",
            "2302",
            "2303",
            "2304",
            "2305",
            "2306",
            "2307",
            "2308",
            "2309",
            "2310",
            "2311",
            "2312",
            "2327",
            "3101",
            "3201",
            "3202",
            "3203",
            "3204",
            "3205",
            "3206",
            "3207",
            "3208",
            "3209",
            "3210",
            "3211",
            "3212",
            "3213",
            "3301",
            "3302",
            "3303",
            "3304",
            "3305",
            "3306",
            "3307",
            "3308",
            "3309",
            "3310",
            "3311",
            "3401",
            "3402",
            "3403",
            "3404",
            "3405",
            "3406",
            "3407",
            "3408",
            "3410",
            "3411",
            "3412",
            "3413",
            "3415",
            "3416",
            "3417",
            "3418",
            "3501",
            "3502",
            "3503",
            "3504",
            "3505",
            "3506",
            "3507",
            "3508",
            "3509",
            "3601",
            "3602",
            "3603",
            "3604",
            "3605",
            "3606",
            "3607",
            "3608",
            "3609",
            "3610",
            "3611",
            "3701",
            "3702",
            "3703",
            "3704",
            "3705",
            "3706",
            "3707",
            "3708",
            "3709",
            "3710",
            "3711",
            "3712",
            "3713",
            "3714",
            "3715",
            "3716",
            "3717",
            "4101",
            "4102",
            "4103",
            "4104",
            "4105",
            "4106",
            "4107",
            "4108",
            "4109",
            "4110",
            "4111",
            "4112",
            "4113",
            "4114",
            "4115",
            "4116",
            "4117",
            "4190",
            "4201",
            "4202",
            "4203",
            "4205",
            "4206",
            "4207",
            "4208",
            "4209",
            "4210",
            "4211",
            "4212",
            "4213",
            "4228",
            "4290",
            "4301",
            "4302",
            "4303",
            "4304",
            "4305",
            "4306",
            "4307",
            "4308",
            "4309",
            "4310",
            "4311",
            "4312",
            "4313",
            "4331",
            "4401",
            "4402",
            "4403",
            "4404",
            "4405",
            "4406",
            "4407",
            "4408",
            "4409",
            "4412",
            "4413",
            "4414",
            "4415",
            "4416",
            "4417",
            "4418",
            "4419",
            "4420",
            "4451",
            "4452",
            "4453",
            "4501",
            "4502",
            "4503",
            "4504",
            "4505",
            "4506",
            "4507",
            "4508",
            "4509",
            "4510",
            "4511",
            "4512",
            "4513",
            "4514",
            "4601",
            "4602",
            "4603",
            "4604",
            "4690",
            "5001",
            "5002",
            "5101",
            "5103",
            "5104",
            "5105",
            "5106",
            "5107",
            "5108",
            "5109",
            "5110",
            "5111",
            "5113",
            "5114",
            "5115",
            "5116",
            "5117",
            "5118",
            "5119",
            "5120",
            "5132",
            "5133",
            "5134",
            "5201",
            "5202",
            "5203",
            "5204",
            "5205",
            "5206",
            "5223",
            "5226",
            "5227",
            "5301",
            "5303",
            "5304",
            "5305",
            "5306",
            "5307",
            "5308",
            "5309",
            "5323",
            "5325",
            "5326",
            "5328",
            "5329",
            "5331",
            "5333",
            "5334",
            "5401",
            "5402",
            "5403",
            "5404",
            "5405",
            "5424",
            "5425",
            "6101",
            "6102",
            "6103",
            "6104",
            "6105",
            "6106",
            "6107",
            "6108",
            "6109",
            "6110",
            "6201",
            "6202",
            "6203",
            "6204",
            "6205",
            "6206",
            "6207",
            "6208",
            "6209",
            "6210",
            "6211",
            "6212",
            "6229",
            "6230",
            "6301",
            "6302",
            "6322",
            "6323",
            "6325",
            "6326",
            "6327",
            "6328",
            "6401",
            "6402",
            "6403",
            "6404",
            "6405",
            "6501",
            "6502",
            "6504",
            "6505",
            "6523",
            "6527",
            "6528",
            "6529",
            "6530",
            "6531",
            "6532",
            "6540",
            "6542",
            "6543",
            "6590",
        ]
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
