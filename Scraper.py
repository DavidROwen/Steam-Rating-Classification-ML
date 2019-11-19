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

start_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998"


def scrape(entry_point, save=False, use_cached=False, links_only=False):
    start_time = time.time()
    try:
        option = webdriver.ChromeOptions()
        option.add_argument(" - incognito")
        browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)
        # browser.implicitly_wait(10)

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
    while True:
        time.sleep(3)
        # Grab elements from the page
        wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable")
        try:
            elements = browser.find_elements_by_xpath("//div[@id='search_resultsRows']//a[contains(@href, 'steampowered.com/app/')]")
        except:
            break

        reviews = browser.find_elements_by_xpath("//div[contains(@class, 'search_reviewscore')]")

        # Extract only the links with a review score to save time later.
        ratings = []
        for review in reviews:
            try:
                spans = review.find_elements_by_xpath(".//span")
                if len(spans) != 0:
                    rating = spans[0].get_attribute("data-tooltip-html").split("<")[0]
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

        print("Time Elapsed: {:.2f}   \tLinks Collected: {}".format(time.time() - start_time, len(game_link_list)))
        # if len(game_link_list) > 20:
        #     break
        # Check if there is any more pages left
        try:
            wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable").click()
        except NoSuchElementException:
            print("No more games!")
            break
    return game_link_list

def wait_till_success(browser, xpath, timeout=4, retry_time=20, wait_time=1, condition="visibility_of_element_located"):
    start_time = time.time()
    found = False
    element = None
    while (time.time() - start_time) < retry_time:
        try:
            element = WebDriverWait(browser, timeout).until(getattr(EC, condition)((By.XPATH, xpath)))
            found = True
            break
        except WebDriverException as e:
            print("Exception when trying to find element: {}, {}".format(xpath, e))
            time.sleep(wait_time)
    if found:
        pass
        # print("Time Elapsed: {:.2f}   \tElement found: {}".format(time.time() - start_time, len(xpath)))
    else:
        # print("Time Elapsed: {:.2f}   \tElement not found: {}".format(time.time() - start_time, len(xpath)))
        pass
        raise WebDriverException
    return element

scrape(start_url, True, False, True)