# -*- coding: utf-8 -*-
import requests

url = "http://127.0.0.1:8000/show/9"
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
lastMemo = html.find("以上。") -3
Memo = html[firstMemo:lastMemo]
print Memo

content = "ID" + Id + "の"
content += "QRコードは" + Qr
content += "、名前は" + Name
content += "、母国語は" + Lang
content += "、メモは" + Memo
content += "です。"
print content