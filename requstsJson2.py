# -*- coding: utf-8 -*-
import requests
from datetime import datetime

url = "http://cms.e-harp.jp/json/123"

def readContent():
  res = requests.get(url)
  if res.text == "There is no data. Please check QR code number.":
    cont = "データがありません。"
    print cont.decode('utf-8')
  else:
    res = res.json()

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
    print content.decode("utf-8")

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

readContent()
