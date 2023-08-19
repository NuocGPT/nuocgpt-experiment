from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import time

url = "https://sotuphap.soctrang.gov.vn/snnptnt/1282/30591/53960/371205/Thong-tin-phuc-vu-San-xuat-Nong-nghiep/THONG-BAO-KET-QUA-QUAN-TRAC-MOI-TRUONG-Tuan-33--Ngay-7-8-8-2023-.aspx"
print(f"Calling Selenium for url {url}")

driver = webdriver.Chrome()
driver.get(url)
driver.implicitly_wait(3.0)

print(driver.title)
print(driver.current_url)

soup = BeautifulSoup(driver.page_source, "html.parser")

total_urls = []

for link in soup.find_all('a'):
    other_day_url = link.get('href')
    if other_day_url is not None:
        if "BAO-KET-QUA-QUAN-TRAC-MOI-TRUONG" in other_day_url and other_day_url not in total_urls:
            print(other_day_url)
            total_urls.append(other_day_url)
            
for page_id in range(2, 10):
    #driver.find_element(By.CLASS_NAME, "ButtonPage").click()
    try:
        el = driver.find_element(By.LINK_TEXT, str(page_id))
        el.click()
        time.sleep(7)
    except NoSuchElementException:
        el_list = driver.find_elements(By.LINK_TEXT, "...")
        if len(el_list) == 1:
            # first page
            el_list[0].click()
        else:
            # every page after, there are two buttons for back and forth, we want the second one
            el_list[1].click()
        time.sleep(7)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    for link in soup.find_all('a'):
        other_day_url = link.get('href')
        if other_day_url is not None:
            if "BAO-KET-QUA-QUAN-TRAC-MOI-TRUONG" in other_day_url or "bao-ket-qua-quan-trac-moi-truong" in other_day_url:
                if other_day_url not in total_urls:
                    print(other_day_url)
                    total_urls.append(other_day_url)

    # if not has_new_url:
    #     break

driver.quit()

with open("soc_trang_urls.txt", "w", encoding="utf-8") as f:
    for url in total_urls:
        f.write(url + "\n")
