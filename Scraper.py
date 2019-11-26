from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import time
import pickle
from ArffBuilder import Game, build_arff_from_games

start_url = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&category1=998"

def scrape(entry_point, save=False, use_cached=False, links_only=False):
    start_time = time.time()
    try:
        option = webdriver.ChromeOptions()
        option.add_argument(" - incognito")
        browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)

        if not use_cached:
            browser.get(entry_point)
            print("### Gathering Links ###")

            # Wait for page to load
            try:
                wait_till_success(browser, "//a[1]//div[1]//img[1]")
            except TimeoutException:
                print("Timed out waiting for page to load")
                browser.quit()

            # Collect the links to each games page
            game_link_list = scrape_links(browser)
            print(game_link_list)
            if save:
                with open('game-store-page-links', 'wb') as fp:
                    pickle.dump(game_link_list, fp)
                    
        else:
            with open ('game-store-page-links', 'rb') as fp:
                game_link_list = pickle.load(fp)

        if not links_only:
            game_data_list = []
            print("### Scraping Game Pages ###")
            # Go to each games page to collect the rating and tag information
            for game in game_link_list:
                game_data = scrape_game_page(browser, game)
                if game_data != []:
                    game_data_list.append(game_data)

            build_arff_from_games(game_data_list)
    finally:
        pass
    #     browser.close()
    print("Total Time Elapsed: {:.2f}".format(time.time() - start_time))


def scrape_game_page(browser, game_link):
    start_time = time.time()
    browser.get(game_link)

    current_game = Game(game_link.split("/")[5])
    current_game.tags = []
    
    # Make sure the page is loaded
    wait_till_success(browser, "//img[@class='game_header_image_full']")
    
    # Check if the game even has rating
    try:
        rating_field = wait_till_success(browser, "//div[@class='summary column']//span[1]")
    except:
        return []
    if "not_enough_reviews" in rating_field.get_attribute("class"):
        return []
    current_game.rating = rating_field.text

    # Open the tag page
    wait_till_success(browser, "//div[@class='app_tag add_button']", condition="element_to_be_clickable").click()

    # Wait till the modal is loaded
    wait_till_success(browser, "//span[contains(text(),'Close')]")
    
    tags = []
    tags = browser.find_elements_by_xpath("//div[@class='app_tag_control popular']//a[@class='app_tag']")
    for tag in tags:
        current_game.tags.append(tag.text)
    
    print("Time Elapsed: {:.2f}   \tGame Collected: {}".format(time.time() - start_time, current_game.name))
    return current_game

def scrape_links(browser):
    start_time = time.time()
    game_link_list = []
    pages = 0
    while True:
        time.sleep(1)
        # Grab elements from the page
        try:
            wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable", refresh=True)
        except WebDriverException:
            print("Refreshing!")
            browser.refresh()
            try:
                wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable")
            except NoSuchElementException:
                print("No more games!")
        
        # Extract only the links with a review score to save time later.
        ratings = []
        xpath_review = ".//div[contains(@class, 'search_reviewscore')]"
        for review_index in range(len(browser.find_elements_by_xpath(xpath_review))):
            retrys = 0
            while retrys < 5:
                try:
                    rating = browser.find_elements_by_xpath(xpath_review)[review_index].find_elements_by_xpath(".//span")[0].get_attribute("data-tooltip-html").split("<")[0]
                except NoSuchElementException:
                    print("Rating not found")
                    rating = ""
                except StaleElementReferenceException:
                    print("Stale so trying again")
                    rating = ""
                retrys += 1
            ratings.append(rating)

        added = False
        xpath_links = ".//div[@id='search_resultsRows']//a[contains(@href, 'steampowered.com/app/') or contains(@href, 'steampowered.com/sub/')]"
        for link_index in range(len(ratings)):
            retrys = 0
            while retrys < 5:
                href = browser.find_elements_by_xpath(xpath_links)[link_index].get_attribute("href").split("/")
                if "?snr" not in href[5] and "sub" not in href[3] and ratings[link_index] != "":
                    added = True
                    game_link_list.append(href)
                    break
                retrys += 1

        pages += 1
        print("Time Elapsed: {:.2f}   \tLinks Collected: {} \tPages: {}".format(time.time() - start_time, len(game_link_list), pages))
        if added == False:
            return game_link_list

        # if len(game_link_list) > 60:
        #     return game_link_list
        # Check if there is any more pages left
        try:
            wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable", refresh=True).click()
        except NoSuchElementException:
            print("No more games found!")
            break

    return game_link_list

def wait_till_success(browser, xpath, timeout=4, retry_time=20, wait_time=1, condition="visibility_of_element_located", refresh=False):
    start_time = time.time()
    found = False
    element = None
    while (time.time() - start_time) < retry_time:
        try:
            element = WebDriverWait(browser, timeout).until(getattr(EC, condition)((By.XPATH, xpath)))
            found = True
            break
        except WebDriverException as e:
            if refresh:
                print("Refreshing!")
                browser.refresh()
                refresh = False
            print("Exception when trying to find element: {}, {}".format(xpath, repr(e)))
            time.sleep(wait_time)
    if not found:
        raise WebDriverException("Element not found")
        
    return element

scrape(start_url, True, False, True)