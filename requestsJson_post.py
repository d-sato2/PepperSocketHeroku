# -*- coding: utf-8 -*-
import requests
from datetime import datetime

url = "http://127.0.0.1:8000/json/1"

goal = {'goal': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
r = requests.post(url, data=goal)
print r.text