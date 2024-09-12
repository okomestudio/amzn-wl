"""Selenium drivers."""

from selenium import webdriver
from selenium_stealth import stealth

from .configs import config


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """Create a webdriver."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver_config = config["driver"] if "driver" in config else {}

    stealth(
        driver,
        user_agent=driver_config["user_agent"],
        languages=driver_config["languages"].split(),
        vendor=driver_config["vendor"],
        platform=driver_config["platform"],
        webgl_vendor=driver_config["webgl_vendor"],
        renderer=driver_config["renderer"],
        fix_hairline=driver_config.getbool("fix_hairline"),
    )

    return driver
