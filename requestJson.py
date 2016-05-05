# -*- coding: utf-8 -*-
import requests
from datetime import datetime

url = "http://127.0.0.1:8000/json/4"
res = requests.get(url).json()
print res
print res["id"]
print res["qr"]
print res["name"]
print res["lang"]
print res["memo"]
print res["start"]

content = "ID" + str(res["id"]) + "の"
content += "QRコードは" + str(res["qr"])
content += "、名前は" + str(res["name"])
content += "、母国語は" + str(res["lang"])
content += "、メモは" + str(res["memo"])
content += "、出発時刻は" + str(res["start"])
content += "です。"
print content

StartTime = str(res["start"])
print StartTime
inttime = datetime.strptime(StartTime, '%Y-%m-%d %H:%M:%S')
print inttime
print inttime.year
print inttime.month
print inttime.day
print inttime.hour
print inttime.minute
print inttime.second