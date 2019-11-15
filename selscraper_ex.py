from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

start_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998"

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)


browser.get("https://github.com/davidrowen")

# Wait 20 seconds for page to load
timeout = 20
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='avatar width-full height-full avatar-before-user-status']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

# find_elements_by_xpath returns an array of selenium objects.
titles_element = browser.find_elements_by_xpath("//a[@class='text-bold']")
# use list comprehension to get the actual repo titles and not the selenium objects.
titles = [x.text for x in titles_element]
# print out all the titles.
print('titles:')
print(titles, '\n')

language_element = browser.find_elements_by_xpath("//p[@class='mb-0 f6 text-gray']")
# same concept as for list-comprehension above.
languages = [x.text for x in language_element]
print("languages:")
print(languages, '\n')

for title, language in zip(titles, languages):
    print("RepoName : Language")
    print(title + ": " + language, '\n')