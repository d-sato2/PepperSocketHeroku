# -*- coding: utf-8 -*-
import requests
from datetime import datetime

url = "http://127.0.0.1:8000/show/4"
response = requests.get(url)
html = response.text.encode(response.encoding)

firstId = html.find("ID : ") + 5
lastId = html.find("の観光客情報")
Id = html[firstId:lastId]
print Id

firstQr = html.find("QRcode : ") + 9
lastQr = html.find("name : ") - 3
Qr = html[firstQr:lastQr]
print Qr

firstName = html.find("name : ") + 7
lastName = html.find("language : ") -3
Name = html[firstName:lastName]
print Name

firstLang = html.find("language : ") + 11
lastLang = html.find("memo : ") -3
Lang = html[firstLang:lastLang]
print Lang

firstMemo = html.find("memo : ") + 7
lastMemo = html.find("start time : ") -3
Memo = html[firstMemo:lastMemo]
print Memo

firstTime = html.find("start time : ") + 13
lastTime = html.find("以上。") -3
StartTime = html[firstTime:lastTime]
print StartTime
inttime = datetime.strptime(StartTime, '%Y-%m-%d %H:%M:%S')
print inttime
print inttime.year
print inttime.month
print inttime.day
print inttime.hour
print inttime.minute
print inttime.second

content = "ID" + Id + "の"
content += "QRコードは" + Qr
content += "、名前は" + Name
content += "、母国語は" + Lang
content += "、メモは" + Memo
content += "、出発時刻は" + StartTime
content += "です。"
print content