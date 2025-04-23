"""Sign-in steps."""

import logging
import os
from getpass import getpass

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


def signin(
    driver: webdriver.Chrome, url: str, max_wait: float = 16, max_retry: int = 1
) -> None:
    """Sign in from given landing URL."""
    username = os.environ.get("AMZN_USERNAME") or input("Enter in your username: ")
    password = os.environ.get("AMZN_PASSWORD") or getpass("Enter in your password: ")

    driver.get(url)

    elmt = None
    try:
        elmt = WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList"))
        )
    except exceptions.TimeoutException:
        logger.warning("Cannot find 'Account & Login' section. Retrying...")
    else:
        elmt.find_elements(By.XPATH, ".//span")[0].click()

    if not elmt:
        try:
            elmt = WebDriverWait(driver, max_wait).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Your Account']"))
            )
        except exceptions.TimeoutException:
            logger.warning("Cannot find 'Your Account' section. Retrying...")
        else:
            elmt.find_elements(By.XPATH, "./span")[0].click()

    if not elmt:
        print(driver.page_source)
        raise RuntimeError("Signin failed")

    # raise RuntimeError("SUCCESS")

    exc = None
    for target in ['ap_email', 'ap_email_login']:
        try:
            WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.ID, target))
            ).send_keys(username)
        except exceptions.TimeoutException as exc:
            continue
        else:
            break
    else:
        if exc:
            raise exc

    WebDriverWait(driver, max_wait).until(
        EC.element_to_be_clickable((By.ID, "continue"))
    ).submit()

    WebDriverWait(driver, max_wait).until(
        EC.presence_of_element_located((By.ID, "ap_password"))
    ).send_keys(password)

    WebDriverWait(driver, max_wait).until(
        EC.element_to_be_clickable((By.ID, "auth-signin-button-announce"))
    ).submit()

    otp_code = os.environ.get("AMZN_OTP") or input("OTP Code: ")

    WebDriverWait(driver, max_wait).until(
        EC.presence_of_element_located((By.ID, "auth-mfa-otpcode"))
    ).send_keys(otp_code)

    WebDriverWait(driver, max_wait).until(
        EC.element_to_be_clickable((By.ID, "auth-signin-button"))
    ).submit()

    elmt = WebDriverWait(driver, max_wait).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@id='nav-link-accountList']//span[@id='nav-link-accountList-nav-line-1']",
            ),
        )
    )
    assert "Sign in" not in elmt.text, "Sign appears to have failed"
