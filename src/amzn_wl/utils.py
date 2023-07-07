"""Utilities."""
import contextlib
import locale
import logging
import random
import time
import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


def sanitize_url(url):
    p = urllib.parse.urlparse(url)
    url = urllib.parse.urlunparse((p.scheme, p.netloc, p.path, None, None, None))
    return url


def wait_random(base: float = 2.0, frac: float = 0.5) -> None:
    t = base + ((base * frac) * random.random() - (base * frac) * 0.5)
    time.sleep(t)


@contextlib.contextmanager
def new_window(driver, action, wait: float = 5):
    base_window = driver.current_window_handle
    base_title = driver.title
    window_handles = driver.window_handles

    action()
    WebDriverWait(driver, wait).until(EC.new_window_is_opened(window_handles))
    driver.switch_to.window(driver.window_handles[1])

    try:
        yield

    except Exception as exc:
        logger.exception(exc)

    finally:
        driver.close()
        driver.switch_to.window(base_window)
        WebDriverWait(driver, wait).until(EC.title_is(base_title))


def get(elmt, xpath, resource=None):
    elmts = elmt.find_elements(By.XPATH, xpath)
    if not elmts:
        return
    elmt = elmts[0]
    if resource is None:
        return elmt
    elif isinstance(resource, str):
        return getattr(elmt, resource)
    elif callable(resource):
        return resource(elmt)
    else:
        raise ValueError("`resource` must be str or callable")


@contextlib.contextmanager
def switch_locale(groups, loc):
    current_locale = ".".join(locale.getlocale())
    for group in groups:
        locale.setlocale(group, loc)

    try:
        yield

    finally:
        for group in groups:
            locale.setlocale(group, current_locale)
