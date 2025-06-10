#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/28 15:28 
# @Author   : guoqun X2590
# @FileName : demo.py
# @Project  : DataForge

from faker import Faker
from faker.providers import internet

fake = Faker(locale="zh_CN")


for _ in range(10):
    print(fake.numerify(("USER-####-####")))
    print(fake.address())
    print(fake.phone_number())
    print(fake.company())
    print(fake.ipv4_public())
    print(fake.ipv4_private())
