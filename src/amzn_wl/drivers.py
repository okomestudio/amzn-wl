from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome()  # options=options
    return driver
