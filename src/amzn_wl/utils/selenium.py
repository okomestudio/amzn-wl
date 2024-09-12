"""Selenium utilities."""

import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def scroll_till_fully_loaded(
    driver: webdriver.Chrome, stop_condition: str, max_try: int = 40, wait: int = 1
) -> None:
    """Scroll down a wishlist page till the end."""
    for _ in range(max_try):
        try:
            WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((By.ID, stop_condition))
            )
        except exceptions.TimeoutException:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            continue
        else:
            break
