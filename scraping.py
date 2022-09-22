from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests


from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week_11

driver = webdriver.Chrome('./chromedriver')

url = "https://www.localdata.go.kr/lif/lifeCtacDataView.do"

driver.get(url)
time.sleep(5)


btn1_more = driver.find_element_by_css_selector("#navigator > a:nth-child(3)")
btn1_more.click()
time.sleep(5)


req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

#etc-data-table > table > tbody > tr:nth-child(1) > td:nth-child(2)
#etc-data-table > table > tbody > tr:nth-child(2) > td:nth-child(2)

#etc-data-table > table > tbody > tr:nth-child(1) > td:nth-child(3)
#etc-data-table > table > tbody > tr:nth-child(2) > td:nth-child(3)

#etc-data-table > table > tbody > tr:nth-child(1) > td:nth-child(3)
#etc-data-table > table > tbody > tr:nth-child(2) > td:nth-child(3)
#etc-data-table > table > tbody > tr:nth-child(3) > td:nth-child(3)

places = soup.select("#etc-data-table > table > tbody > tr")
print(len(places))

for place in places:
    title = place.select_one("td:nth-child(2)").text
    address = place.select_one("td:nth-child(3)").text
    print(title, address)

    headers = {
        "X-NCP-APIGW-API-KEY-ID": "ygin9u6wg5",
        "X-NCP-APIGW-API-KEY": "Pw2pMFI6xbMxiIPwetx4y0Ir7biYPrWXatpsaKRQ"
    }
    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}", headers=headers)
    response = r.json()
    if response["status"] == "OK":
        if len(response["addresses"]) > 0:
            x = float(response["addresses"][0]["x"])
            y = float(response["addresses"][0]["y"])
            print(title, address, x, y)
            doc = {
                "title": title,
                "address": address,
                "mapx": x,
                "mapy": y}
            db.toilet.insert_one(doc)

        else:
            print(title, "좌표를 찾지 못했습니다")