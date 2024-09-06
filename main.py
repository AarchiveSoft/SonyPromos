"""
intended to scrape website sony promotion overview and extract relevant data to be represented in a consise gui

start with scraping

TODO:
- GUI
- search by product
- visually appealing and understandable table view or simular
- clearly indicate conditions for promotions
"""
import cmath
import datetime

import sys
import os

import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    """
    Main Method

    This method serves as the entry point of the program. It creates an object of the DataBase class, initializes the database, scrapes information using the database object, and prints the results.

    :return: None
    """
    db = DataBase()  # Create an object of the DataBase class
    db.create_database()
    scrape_info(db)  # Passes the object of DataBase into function
    db.print_results()


class DataBase:
    """
    :class: DataBase

    This class represents a database that stores promotional information about Sony products.

    Attributes:
        conn (:obj:`sqlite3.Connection`): The connection object to the database.
        c (:obj:`sqlite3.Cursor`): The cursor object to execute SQL statements.

    Methods:
        **__init__**()
            Initializes the database connection.

        **create_database**()
            Creates the 'promos' table if it does not already exist.

        **print_results**()
            Prints all rows in the 'promos' table.

    Usage:
        Instantiate the DataBase class to create a connection to the database. Call the `create_database` method to create the 'promos' table. Call the `print_results` method to print the rows in the 'promos' table.
    """

    def __init__(self):
        self.conn = sqlite3.connect('sonyPromos.db')
        self.c = self.conn.cursor()

    def create_database(self):
        self.c.execute('''
                CREATE TABLE IF NOT EXISTS promos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    promo_title TEXT,
                    promo_details TEXT,
                    model TEXT,
                    art_nr TEXT,
                    start_date DATE,
                    end_date DATE,
                    scrape_date DATE,
                    product_link TEXT,
                    promo_link TEXT
                )
            ''')

    def print_results(self):
        print("Results:")
        self.c.execute('SELECT * FROM promos')
        rows = self.c.fetchall()
        for row in rows:
            print(row)


def scrape_info(db):
    """
    This method scrapes information from a website and stores it in a database.

    :return: None
    """

    if getattr(sys, "frozen", False):
        # Running as packaged executable, driver is in same directory
        base_path = sys._MEIPASS
    else:
        # Running as normal script, driver is in parent directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)
    chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
    chrome_options = ChromeOptions()
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
    category_list = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".x-grid.e9902-e5.m7n2-0")))
    category_elements = category_list.find_elements(By.CLASS_NAME, "x-cell")

    category_links = []

    for category in category_elements:
        category_link = category.find_element(By.TAG_NAME, "a").get_attribute("href")
        category_links.append(category_link)

    # go through each category and gather necessary information

    for category_link in category_links:
        driver.get(category_link)

        promo_title_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".x-text.cs-ta-center")))
        promo_title_string = promo_title_element.find_element(By.TAG_NAME, "h4").text

        promo_description_element = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "p:nth-child(1) strong:nth-child(1)")))
        promo_description_string = promo_description_element.text

        promo_text_element = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".x-text.x-content.e16127-e6.mcfz-0")))
        promo_text_block_titles = promo_text_element.text

        non_empty_titles = [
            title
            for title in promo_text_block_titles
            if title.text.strip() not in ['', '\xa0']
        ]
        titles_to_process = non_empty_titles[2:]

        title_and_contents = {}

        for title in titles_to_process:
            title_text = title.text

            try:
                ul_sibling = title.find_element(By.XPATH, "./following-sibling::ul")
                li_elements = ul_sibling.find_elements(By.TAG_NAME, "li")

                entry_text = [li.text for li in li_elements]

                title_and_contents[title_text] = entry_text
            except Exception as e:
                print(f"error: {e}")
                continue

            for key, list_values in title_and_contents.items():
                db.c.execute('''
                    INSERT INTO promos (promo_title, promo_details, promo_link, scrape_date)
                    VALUES (?, ?, ?, ?)
                ''', (key, promo_description_string, category_link, datetime.date.today()))

                for value in list_values:
                    db.c.execute('''
                        INSERT INTO promos (model)
                        VALUES (?)
                    ''', (value,))
            db.conn.commit()

        driver.quit()


if __name__ == "__main__":
    main()
