from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.get("https://travinh.gov.vn/mDefault.aspx?sid=1444&pageid=6591&catid=71012&id=693472&catname=ket-qua-quan-trac-moi-truong-nuoc&title=ket-qua-quan-trac-moi-truong-nuoc-ngay-15-8-2023-tren-dia-ban-tinh-tra-vinh")
driver.implicitly_wait(3.0)

print(driver.title)
print(driver.current_url)

soup = BeautifulSoup(driver.page_source, "html.parser")

for link in soup.find_all('a'):
    other_day_url = link.get('href')
    if other_day_url is not None:
        if "ket-qua-quan-trac-moi-truong-nuoc-ngay" in other_day_url:
            print(other_day_url)
            
            
driver.find_element(By.CLASS_NAME, "ButtonPage").click()
#driver.find_element(By.LINK_TEXT,"2").click()
# driver.implicitly_wait(30.0)
time.sleep(2)

soup = BeautifulSoup(driver.page_source, "html.parser")

for link in soup.find_all('a'):
    other_day_url = link.get('href')
    if other_day_url is not None:
        if "ket-qua-quan-trac-moi-truong-nuoc-ngay" in other_day_url:
            print(other_day_url)

driver.quit()