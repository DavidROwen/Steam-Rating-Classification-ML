from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from multiprocessing import Process, Queue, Pool
from os import getpid
import time
import pickle
from ArffBuilder import Game, build_arff_from_games

start_url = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&category1=998"

def scrape(entry_point, save=False, use_cached=False, links_only=False):
    start_time = time.time()
    if not use_cached:
        try:
            print("### Gathering Links ###")
            option = webdriver.ChromeOptions()
            option.add_argument(" - incognito")
            browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)

            # Collect the links to each games page
            game_link_list = scrape_links(browser)
            if save:
                with open('game-store-page-links', 'wb') as fp:
                    pickle.dump(game_link_list, fp)
        finally:
            browser.close()     
    else:
        with open ('game-store-page-links', 'rb') as fp:
            game_link_list = pickle.load(fp)

    game_links = []
    for game in game_link_list:
        game_links.append("/".join(game[:-1]))

    if not links_only:
        thread_game_pages(game_links, start_time)

    print("Total Time Elapsed: {:.2f}".format(time.time() - start_time))

def chunkify(l, n):
    # Yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def thread_game_pages(game_links, start_time):
    print("### Scraping Game Pages ###")
    print("{} Games to collect".format(len(game_links)))
    
    chunked = chunkify(game_links, 50)

    game_data_list = []
    pool = Pool(processes = 4)
    result_list = pool.map(scrap_chunk_of_pages, chunked)

    # Flatten the list
    results = [item for sublist in result_list for item in sublist]

    build_arff_from_games(results)

def scrap_chunk_of_pages(chunk):
    start_time = time.time()
    option = webdriver.ChromeOptions()
    option.add_argument(" - incognito")
    prefs = {'profile.managed_default_content_settings.images':2 , 'disk-cache-size': 4096}
    option.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=option)
    
    # print("{} Processing: {}".format(getpid(), chunk))
    # print("{} Processing".format(getpid()))
    
    result = []
    try:
        for game in chunk:
            success = False
            for _ in range(5):
                try:
                    game_data = scrape_game_page(browser, game)
                    if game_data != []:
                        result.append(game_data)
                    success = True
                    break
                except Exception as e:
                    print("Page parse failed: {}   Exception {}".format(game, e))
            if not success:
                game_data = scrape_game_page(browser, game)
                if game_data != []:
                    result.append(game_data)
            # [print("{} collected {} games so far".format(getpid(), len(result)))]
    except Exception as e:
        print("Exception!!! {}".format(e))
    finally:
        browser.close()
    print("{} got {} games in {:.2f} seconds".format(getpid(), len(result), time.time() - start_time))
    return result

def scrape_game_page(browser, game_link):
    browser.get(game_link)
    time.sleep(1)
    current_game = Game(game_link.split("/")[5])
    current_game.tags = []
    
    result = browser.find_elements_by_xpath("//h2[contains(text(),'This Game may contain content not appropriate for')]")
    if result != []:
        # print("Mature Game: {}, Ignoring".format(current_game.name))
        return ([])

    # Make sure the page is loaded
    wait_till_success(browser, "//div[@class='app_tag add_button']", condition="element_to_be_clickable", refresh=True)
    # wait_till_success(browser, "//img[@class='game_header_image_full']", refresh=True)
    
    # Check if the game even has rating
    try:
        rating_field = wait_till_success(browser, "//div[@class='summary column']//span[1]")
    except:
        return ([])
    if "not_enough_reviews" in rating_field.get_attribute("class"):
        return ([])
    current_game.rating = rating_field.text

    for _ in range(5):
        try:
            # Open the tag page
            clicked = False
            for _ in range(5):
                try:
                    wait_till_success(browser, "//div[@class='app_tag add_button']", condition="element_to_be_clickable").click()
                    clicked = True
                    break
                except:
                    time.sleep(.5)
            if not clicked:
                raise WebDriverException("Couldn't open modal")


            # Wait till the modal is loaded
            wait_till_success(browser, "//span[contains(text(),'Close')]", condition="element_to_be_clickable")

            tags = []
            tags = browser.find_elements_by_xpath("//div[@class='app_tag_control popular']//a[@class='app_tag']")
            for tag_index in range(len(tags)):
                current_game.tags.append(browser.find_elements_by_xpath("//div[@class='app_tag_control popular']//a[@class='app_tag']")[tag_index].text)
            break
        except NoSuchElementException:
            print("No such element exception")
            browser.refresh()        
        except StaleElementReferenceException:
            print("Stale element exception")
            browser.refresh()
    return current_game

def scrape_links(browser):
    start_time = time.time()
    game_link_list = []
    max_pages = 806
    base_link = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&category1=998&page="
    # Grab elements from each page
    for page in range(1, max_pages + 1):
        browser.get(base_link + str(page))
        
        try:
            if page != max_pages:
                wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable", refresh=True)
        except WebDriverException:
            # print("Refreshing!")
            browser.refresh()
            try:
                wait_till_success(browser, "//a[contains(text(),'>')]", condition="element_to_be_clickable")
            except NoSuchElementException:
                print("No more games!")
        
        # Extract only the links with a review score to save time later.
        ratings = []
        xpath_review = ".//div[contains(@class, 'search_reviewscore')]"
        for review_index in range(len(browser.find_elements_by_xpath(xpath_review))):
            for _ in range(5):
                try:
                    rating = browser.find_elements_by_xpath(xpath_review)[review_index].find_elements_by_xpath(".//span")[0].get_attribute("data-tooltip-html").split("<")[0]
                except NoSuchElementException:
                    print("Rating not found")
                    rating = ""
                except StaleElementReferenceException:
                    print("Stale so trying again")
                    rating = ""
                except IndexError:
                    # print("Refreshing!")
                    browser.refresh()
            ratings.append(rating)

        xpath_links = ".//div[@id='search_resultsRows']//a[contains(@href, 'steampowered.com/app/') or contains(@href, 'steampowered.com/sub/')]"
        for link_index in range(len(ratings)):
            for _ in range(5):
                try:
                    href = browser.find_elements_by_xpath(xpath_links)[link_index].get_attribute("href").split("/")
                    if "?snr" not in href[5] and "sub" not in href[3] and ratings[link_index] != "":
                        game_link_list.append(href)
                        break
                except StaleElementReferenceException:
                    print("Stale so trying again")

        print("Time Elapsed: {:.2f}   \tLinks Collected: {} \tPages: {}".format(time.time() - start_time, len(game_link_list), page))
        
        if page == max_pages:
            print("Last page reached")

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
                # print("Refreshing!")
                browser.refresh()
                refresh = False
            # print("Exception when trying to find element: {}, {}".format(xpath, repr(e)))
            time.sleep(wait_time)
    if not found:
        raise WebDriverException("Element not found: {}".format(xpath))
        
    return element

scrape(start_url, save=False, use_cached=True, links_only=False)