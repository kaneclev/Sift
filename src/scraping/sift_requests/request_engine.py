import os
import pickle
import time

import undetected_chromedriver as uc

from curl_cffi import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth

from scraping.sift_requests.request_logger import Logger

cookies_dir = os.environ["COOKIES"]
logs = os.environ["SCRAPE_LOGS"]

class TargetRequest:
    def __init__(self, url: str, targ_name: str):
        self.name = targ_name
        self.url = url

        self.logger = Logger.get(self.name)
        self.session = self.get_session()
        self.cookies = None
        self.cookie_file = (os.path.join(cookies_dir, self.name)) + ".pk"

    def make_request(self):
        self.logger.info(f'Making request to url: {self.url}....')
        response = self.session.get(self.url)
        self.save_cookies(response.cookies)
        self.load_cookies()
        self.logger.info(f'Recieved response: {response.text} with status: {response.status_code}')
        return response

    def get_session(self, timeout: float = 5.0) -> requests.Session:
        new_session = requests.Session(timeout=timeout, impersonate="chrome", default_headers=True)
        self.logger.info("Created session...")
        return new_session

    def save_cookies(self, cookies):
        with open(self.cookie_file, "wb") as cookie_f:
            pickle.dump(cookies.jar._cookies, cookie_f)
    def load_cookies(self):
        if not os.path.isfile(self.cookie_file):
            return None
        with open(self.cookie_file, "rb") as cookie_f:
            self.session.cookies.jar._cookies.update(pickle.load(cookie_f))


class BrowserRequest:
    def __init__(self, url: str, targ_name: str):
        self.name = targ_name
        self.url = url
        self.logger = Logger.get(self.name)
        self.cookie_file = os.path.join(cookies_dir, self.name) + ".pk"
        self.driver = self.get_driver()

    def get_driver(self) -> uc.Chrome:
        """
        Creates and returns an undetected-chromedriver Chrome instance.
        This version uses the new headless mode and additional options to help evade detection.
        """
        options = uc.ChromeOptions()
        options.headless = False
        # Set a realistic user-agent.
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/133.0.0.0 Safari/537.36")
        # Set window size to mimic a typical desktop.
        options.add_argument("--window-size=1920,1080")

        self.logger.info("Creating undetected Chrome driver in new headless mode...")
        driver = uc.Chrome(options=options)
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

        return driver

    def load_cookies(self):
        """
        Loads cookies from the cookie file and adds them to the current browser session.
        Note: You must be on a page with a matching domain before adding cookies.
        """
        if not os.path.isfile(self.cookie_file):
            self.logger.info("No cookie file found; skipping cookie load.")
            return

        self.logger.info("Loading cookies from file...")
        with open(self.cookie_file, "rb") as cookie_f:
            cookies = pickle.load(cookie_f)

        # Add each cookie to the browser.
        for cookie in cookies:
            try:
                # Ensure cookie has a sameSite attribute (Selenium may expect one)
                if "sameSite" not in cookie:
                    cookie["sameSite"] = "Strict"
                self.driver.add_cookie(cookie)
            except Exception as e:
                self.logger.error(f"Error adding cookie {cookie.get('name')}: {e}")

    def save_cookies(self):
        """
        Saves the current browser session cookies to a file.
        """
        cookies = self.driver.get_cookies()
        with open(self.cookie_file, "wb") as cookie_f:
            pickle.dump(cookies, cookie_f)
        self.logger.info("Saved cookies to file.")

    def make_request(self):
        """
        Navigates to the URL, loads any stored cookies (after an initial navigation to set the domain),
        refreshes the page to apply cookies, waits for page load, and then saves any updated cookies.
        Returns the page source.
        """
        self.logger.info(f"Navigating to URL: {self.url} ...")
        # First, open the URL so that the domain is loaded.
        self.driver.get(self.url)

        # Load cookies if available.
        self.load_cookies()

        # Refresh the page to apply the cookies.
        self.logger.info("Refreshing page to apply cookies...")
        self.driver.refresh()

        # Wait for page load (or a specific element) using Selenium's explicit wait.
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")

        # Allow any additional JS requests to complete.
        time.sleep(30)

        page_source = self.driver.page_source
        self.logger.info(f"Retrieved page source of length {len(page_source)}")

        # Save updated cookies.
        self.save_cookies()

        return page_source

    def quit(self):
        """
        Closes the browser and quits the driver.
        """
        self.logger.info("Closing the browser...")
        self.driver.quit()
