"""
intended to scrape website sony promotion overview and extract relevant data to be represented in a consise gui

start with scraping

TODO:
- GUI
- search by product
- visually appealing and understandable table view or simular
- clearly indicate conditions for promotions
"""

import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import by
from selenium.webdriver.chrome import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def createDatabase():
    """
    Create the database and the 'promos' table if it does not exist.

    :return: None
    """
    conn = sqlite3.connect('sonyPromos.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            art_nr TEXT NOT NULL,
            model TEXT,
            promo_details TEXT,
            start_date DATE,
            end_date DATE,
            scrape_date DATE,
            product_link TEXT,
            promo_title TEXT,
            promo_link TEXT
        )
    ''')


def scrape_info():
    if getattr(sys, "frozen", False):
        # Running as packaged executable, driver is in same directory
        base_path = sys._MEIPASS
    else:
        # Running as normal script, driver is in parent directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.path.join(base_path, 'chrome', 'win64-118.0.5993.70', 'chrome-win64',
                                                  'chrome.exe')

    service = Service(chromedriver_path)

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(r"https://www.graphicart.ch/de/uebersicht-sony-aktionen/")
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    wait = WebDriverWait(driver, 10)

    # get category links

