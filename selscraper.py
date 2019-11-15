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

# game_link_list = []
# game_link_list = browser.find_elements_by_xpath("//div[@id='search_resultsRows'//a[1]]")
game_link_list = browser.find_elements_by_xpath("//a[@class='search_result_row']")

try:
# p_links = browser.find_elements_by_xpath("//div[@id='search_resultsRows']")
# for link in p_links:
#   print ("URL: " +link.get_attribute("href"))

    print(game_link_list)
finally:
    browser.close()

# count_per_scroll = 25
# total_text = browser.find_elements_by_xpath("//div[@id='search_results_filtered_warning_persistent']//div")[0].text
# total_results = int(total_text.split()[0].replace(",", ""))


# for _ in range((total_results / count_per_scroll) + 1):
#      ((JavascriptExecutor)
# driver).executeScript(“window.scrollTo(0,
# document.body.scrollHeight)”)

# SCROLL_PAUSE_TIME = 0.5

# # Get scroll height
# last_height = browser.execute_script("return document.body.scrollHeight")

# while True:
#     # Scroll down to bottom
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load page
#     time.sleep(SCROLL_PAUSE_TIME)

#     # Calculate new scroll height and compare with last scroll height
#     new_height = browser.execute_script("return document.body.scrollHeight")
#     if new_height == last_height:
#         break
#     last_height = new_height


# # find_elements_by_xpath returns an array of selenium objects.
# titles_element = browser.find_elements_by_xpath("//a[@class='text-bold']")
# # use list comprehension to get the actual repo titles and not the selenium objects.
# titles = [x.text for x in titles_element]
# # print out all the titles.
# print('titles:')
# print(titles, '\n')

# language_element = browser.find_elements_by_xpath("//p[@class='mb-0 f6 text-gray']")
# # same concept as for list-comprehension above.
# languages = [x.text for x in language_element]
# print("languages:")
# print(languages, '\n')

# for title, language in zip(titles, languages):
#     print("RepoName : Language")
#     print(title + ": " + language, '\n')