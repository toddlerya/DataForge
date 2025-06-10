#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/29 16:00
# @Author   : guoqun X2590
# @FileName : llm_debug.py
# @Project  : DataForge


records = [
    {
        "address": {
            "area_code": "371502101297",
            "area_name": "山东,聊城,东昌府,沙镇,小吕",
            "city_code": "0635",
            "lat": "36.338237",
            "lng": "115.791973",
            "name": "小吕村委会",
            "short_name": "小吕",
            "zip_code": "252032",
        }
    },
    {
        "address": {
            "area_code": "632822100208",
            "area_name": "青海,海西,都兰,察汉乌苏,上滩东",
            "city_code": "0977",
            "lat": "36.301119",
            "lng": "98.090831",
            "name": "上滩东村委会",
            "short_name": "上滩东",
            "zip_code": "816199",
        }
    },
    {
        "address": {
            "area_code": "451424205205",
            "area_name": "广西,崇左,大新,恩城,如龙",
            "city_code": "1771",
            "lat": "22.735910",
            "lng": "107.096186",
            "name": "如龙村民委员会",
            "short_name": "如龙",
            "zip_code": "532311",
        }
    },
    {
        "address": {
            "area_code": "420902101211",
            "area_name": "湖北,孝感,孝南,孝南区西河,双堰",
            "city_code": "0712",
            "lat": "31.003230",
            "lng": "114.018159",
            "name": "双堰村委会",
            "short_name": "双堰",
            "zip_code": "432013",
        }
    },
    {
        "address": {
            "area_code": "610323106202",
            "area_name": "陕西,宝鸡,岐山,青化,凤家庄",
            "city_code": "0917",
            "lat": "34.408778",
            "lng": "107.819450",
            "name": "凤家庄村委会",
            "short_name": "凤家庄",
            "zip_code": "722402",
        }
    },
    {
        "address": {
            "area_code": "230231105211",
            "area_name": "黑龙江,齐齐哈尔,拜泉,国富,卫民",
            "city_code": "0452",
            "lat": "47.686409",
            "lng": "126.337441",
            "name": "卫民村民委员会",
            "short_name": "卫民",
            "zip_code": "164703",
        }
    },
    {
        "address": {
            "area_code": "330602101233",
            "area_name": "浙江,绍兴,越城,灵芝,大庆寺",
            "city_code": "0575",
            "lat": "30.086804",
            "lng": "120.533014",
            "name": "大庆寺村委会",
            "short_name": "大庆寺",
            "zip_code": "312066",
        }
    },
    {
        "address": {
            "area_code": "410522105211",
            "area_name": "河南,安阳,安阳,柏庄,后林都",
            "city_code": "0372",
            "lat": "36.208688",
            "lng": "114.372285",
            "name": "后林都村民委员会",
            "short_name": "后林都",
            "zip_code": "455111",
        }
    },
    {
        "address": {
            "area_code": "410727200000",
            "area_name": "河南,新乡,封丘,城关",
            "city_code": "0373",
            "lat": "35.041198",
            "lng": "114.418882",
            "name": "城关乡",
            "short_name": "城关",
            "zip_code": "453399",
        }
    },
    {
        "address": {
            "area_code": "371122120200",
            "area_name": "山东,日照,莒县,果庄,前果庄村",
            "city_code": "0633",
            "lat": "35.778071",
            "lng": "118.745254",
            "name": "前果庄村村委会",
            "short_name": "前果庄村",
            "zip_code": "276533",
        }
    },
]

data = dict()
keys = records[0]["address"].keys()
print(keys)
for key in keys:
    data[key] = []
for record in records:
    item = record["address"]
    for k, v in item.items():
        data[k].append(v)
print(data)
