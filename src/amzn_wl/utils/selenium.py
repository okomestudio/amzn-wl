"""Selenium utilities."""

import logging
import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


def scroll_till_fully_loaded(
    driver: webdriver.Chrome, stop_condition: str, max_try: int = 50, wait: int = 1.5
) -> None:
    """Scroll down a wishlist page till the end."""
    for trial in range(max_try):
        try:
            WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((By.ID, stop_condition))
            )
        except exceptions.TimeoutException:
            logger.info(f"Scrolling to find stop condition... ({trial + 1}/{max_try})")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(wait)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            continue
        else:
            break
