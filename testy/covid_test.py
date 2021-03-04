import requests
from datetime import datetime

url = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakaza.min.json"

r = requests.get(url)
data = r.json()["data"]

today = datetime.today()
_today = today.strftime("%Y-%m-%d")

#if (data[len(data)-1] == _today):
print(data[len(data)-1]["prirustkovy_pocet_nakazenych"])
    


