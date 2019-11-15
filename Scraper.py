from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time

start_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998"

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)


browser.get(start_url)

# Wait 10 seconds for page to load
timeout = 10
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[1]//div[1]//img[1]")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

game_link_list = []
while True:
    # Grab elements from the page
    elements = browser.find_elements_by_xpath("//a[contains(@href, 'steampowered.com/app/')]")

    # Extract only the links
    for link in elements:
            game_link_list.append(link.get_attribute("href"))

    # Check if there is any more pages left
    try:
        browser.find_element(By.XPATH, "//a[contains(text(),'>')]").click()
        time.sleep(1)
    except:
        break

print(len(game_link_list))
browser.close()
