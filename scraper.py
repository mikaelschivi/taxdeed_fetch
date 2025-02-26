from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

import logging

from time import perf_counter

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def builder(post_json):
    options = Options()
    options.add_argument("--headless")  # headless mode     
    
    s = perf_counter()
    auction = fetch_website_data(post_json["url"], options)
    e = perf_counter()
        
    print(f"elapsed time: {(e - s):.4}s")
    return auction

def fetch_website_data(url, options):
    try:
        driver = webdriver.Firefox(options=options)
        driver.get(url)   
        
        # setup max wait time for element/other shit to load 
        wait = WebDriverWait(driver, 2)

        # wait until the page loads the max page number
        wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "#maxWA").text.strip() != "")    

        nextpage_button = driver.find_element(By.CSS_SELECTOR, "#BID_WINDOW_CONTAINER > div.Head_W > div:nth-child(3) > span.PageRight")
        max_pages = driver.find_element(By.CSS_SELECTOR, "#maxWA").text
        max_pages = int(max_pages.strip())

        auction = []
        for _ in range(max_pages):
            wait.until(lambda d: d.find_element(By.XPATH, "/html/body/table/tbody/tr/td[2]/div[3]/div[3]/div[4]/div[1]/div[1]/div[2]").text.strip() != "")
            items = extract_auction_items(driver)
            for auction_item in items: 
                auction.append(auction_item)
            nextpage_button.click()

        print(auction)
        return auction
    
    except Exception as err:
        print("fuck asfuck:", err)

    finally:    
        driver.quit()

def extract_auction_items(driver):
    items = []
    cards = driver.find_elements(By.CSS_SELECTOR, '#Area_W > .AUCTION_ITEM.PREVIEW')

    for card in cards:
        auction_info = {}
        
        # Extract auction start date
        start_date_element = card.find_element(By.CSS_SELECTOR, '.ASTAT_MSGB')
        auction_info["start_date"] = start_date_element.text.strip()
        
        # Extract auction details
        details = card.find_elements(By.CSS_SELECTOR, '.AUCTION_DETAILS .ad_tab tbody tr')
        for detail in details:
            label_element = detail.find_element(By.CSS_SELECTOR, '.AD_LBL')
            data_element = detail.find_element(By.CSS_SELECTOR, '.AD_DTA')
            
            label = label_element.text.strip().lower().replace('#', '').replace(':', '').replace(' ', '_')
            data = data_element.text.strip()
            
            if label == "case_number":
                auction_info["case_number"] = data
            elif label == "opening_bid":
                auction_info["opening_bid"] = data
            elif label == "parcel_id":
                auction_info["parcel_id"] = data_element.find_element(By.TAG_NAME, 'a').text.strip()
            elif label == "property_address":
                auction_info["property_address"] = data
            elif label == "":  # Complement address
                auction_info["complement"] = data
        
        items.append(auction_info)
    
    return items