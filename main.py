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