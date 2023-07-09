"""Selenium drivers."""
from selenium import webdriver


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a webdriver."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver
