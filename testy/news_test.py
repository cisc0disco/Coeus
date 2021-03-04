from bs4 import BeautifulSoup
import requests

url = "https://www.novinky.cz/zahranicni/svet"
page = requests.get(url)
content = page.content
soup = BeautifulSoup(content)
headers = soup.findAll("h3", {'data-dot-data': '{"component":"mol-feed-item-title","action":"mol-feed-item-title-click"}'})
titulky = ""
for header in headers:
    if ("ON-LINE: " in header.getText()):
        titulky += header.getText().replace("ON-LINE: ", "") + "\n"
    else:
        titulky += header.getText() + "\n"

print(titulky)