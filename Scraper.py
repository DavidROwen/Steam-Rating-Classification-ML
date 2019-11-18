from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
import time
from ArffBuilder import Game, build_arff_from_games

start_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998"

def scrape(entry_point):
    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")
    browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)
    browser.get(entry_point)

    # Wait 10 seconds for page to load
    timeout = 10
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//a[1]//div[1]//img[1]")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    start_time = time.time()
    game_link_list = []
    while True:
        # ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        # your_element = WebDriverWait(browser, timeout=5,ignored_exceptions=ignored_exceptions)\
        #                 .until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'>')]")))
        
        # Grab elements from the page
        elements = browser.find_elements_by_xpath("//a[contains(@href, 'steampowered.com/app/')]")

        # Extract only the links
        for link in elements:
            if "?snr" not in link.get_attribute("href").split("/")[5]:
                game_link_list.append(link.get_attribute("href"))

        print("Time Elapsed: {}   \tLinks Collected: {}".format(time.time() - start_time, len(game_link_list)))
        break
        # Check if there is any more pages left
        try:
            browser.find_element(By.XPATH, "//a[contains(text(),'>')]").click()
            time.sleep(1.0)
        except:
            break
    
    game_data_list = []
    for game in game_link_list:
        browser.get(game)
        game_name = game.split("/")[5]
        current_game = Game(game_name)

        # Wait 10 seconds for page to load
        timeout = 10
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='game_header_image_full']")))
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()
        try:
            rating_field = browser.find_element(By.XPATH, "//div[@class='summary column']//span[1]")
            if "not_enough_reviews" in rating_field.get_attribute("class"):
                continue
            rating = rating_field.text
        except NoSuchElementException:
            continue

        current_game.rating = rating
        browser.find_element(By.XPATH, "//div[@class='app_tag add_button']").click()

        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Close')]")))
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()
        
        tags = browser.find_elements_by_xpath("//div[@class='app_tag_control popular']//a[@class='app_tag']")

        for tag in tags:
            current_game.tags.append(tag.text)
        
        game_data_list.append(current_game)
        
    build_arff_from_games(game_data_list)
    # print(game_data_list[0].name)        
    # print(game_data_list[0].rating)        
    # print(game_data_list[0].tags)        

    # print(len(game_link_list))

    # for game in game_link_list:
    #     print(game)
    browser.close()

scrape(start_url)