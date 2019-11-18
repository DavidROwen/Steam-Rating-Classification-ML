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
    print("### Gathering Links ###")

    # Wait for page to load
    try:
        WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//a[1]//div[1]//img[1]")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    # Collect the links to each games page
    game_link_list = scrape_links(browser)
    
    game_data_list = []
    print("### Scraping Game Pages ###")
    # Go to each games page to collect the rating and tag information
    for game in game_link_list:
        print(game)
        game_data = scrape_game_page(browser, game)
        if game_data != []:
            game_data_list.append(game_data)

    build_arff_from_games(game_data_list)
    browser.close()

def scrape_game_page(browser, game_link):
    start_time = time.time()
    browser.get(game_link)

    current_game = Game(game_link.split("/")[5])
    current_game.tags = []
    
    # Make sure the page is loaded
    try:
        WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='game_header_image_full']")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    
    # Check if the game even has rating
    try:
        rating_field = browser.find_element(By.XPATH, "//div[@class='summary column']//span[1]")
        if "not_enough_reviews" in rating_field.get_attribute("class"):
            return []
        rating = rating_field.text
        current_game.rating = rating
    except NoSuchElementException:
        return []

    while True:
        try:
            browser.find_element(By.XPATH, "//div[@class='app_tag add_button']").click()
            break
        except Exception:
            time.sleep(1)
            continue

    try:
        WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Close')]")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
    
    tags = []
    tags = browser.find_elements_by_xpath("//div[@class='app_tag_control popular']//a[@class='app_tag']")
    for tag in tags:
        current_game.tags.append(tag.text)
    
    print("Time Elapsed: {}   \tGame Collected: {}".format(time.time() - start_time, current_game.name))
    return current_game

def scrape_links(browser):
    start_time = time.time()
    game_link_list = []
    while True:
        # Grab elements from the page
        WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(),'>')]")))
        elements = browser.find_elements_by_xpath("//div[@id='search_resultsRows']//a[contains(@href, 'steampowered.com/app/')]")
        reviews = browser.find_elements_by_xpath("//div[contains(@class, 'search_reviewscore')]")

        # Extract only the links with a review score to save time later.
        ratings = []
        print(reviews)
        for review in reviews:
            try:
                spans = review.find_elements_by_xpath(".//span")
                if len(spans) != 0:
                    rating = spans[0].get_attribute("data-tooltip-html").split("<")[0]
                    print(rating)
                else:
                    rating = ""
            except NoSuchElementException:
                print("Exception")
                rating = ""
            finally:
                ratings.append(rating)

        for rating, link in zip(ratings, elements):
            if "?snr" not in link.get_attribute("href").split("/")[5] and rating != "":
                game_link_list.append(link.get_attribute("href"))

        print("Time Elapsed: {}   \tLinks Collected: {}".format(time.time() - start_time, len(game_link_list)))
        break
        # Check if there is any more pages left
        try:
            WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(),'>')]")))
            browser.find_element(By.XPATH, "//a[contains(text(),'>')]").click()
            time.sleep(2.5)
            print("clicked")
        except:
            print("No more games!")
            break
    return game_link_list

scrape(start_url)