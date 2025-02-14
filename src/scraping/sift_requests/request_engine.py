import os
import pickle

from curl_cffi import requests

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
