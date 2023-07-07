"""Sign-in steps."""
import os
from getpass import getpass

from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def signin(driver, url: str, max_wait: float = 10):
    """Sign in from given landing URL."""
    username = os.environ.get("AMZN_USERNAME") or input("Enter in your username: ")
    password = os.environ.get("AMZN_PASSWORD") or getpass("Enter in your password: ")

    for _ in range(3):
        driver.get(url)
        try:
            elmt = WebDriverWait(driver, max_wait).until(
                EC.presence_of_element_located((By.ID, "nav-link-accountList"))
            )
        except exceptions.TimeoutException:
            continue
        else:
            break

    elmt.find_elements(By.XPATH, "./span")[0].click()

    WebDriverWait(driver, max_wait).until(
        EC.presence_of_element_located((By.ID, "ap_email"))
    ).send_keys(username)

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
                "//a[@id='nav-link-accountList']//span[@id='nav-link-accountList-nav-line-1']",
            ),
        )
    )
    assert "Sign in" not in elmt.text, "Sign appears to have failed"
