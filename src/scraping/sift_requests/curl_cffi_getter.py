from typing import Any, Dict
import io
import curl_cffi

from scraping.sift_requests.content import SiteContent
from scraping.sift_requests.getter import Getter
from scraping.sift_requests.properties import Headers, UserAgents


class CurlCffiRequest(Getter):
    settings = {
        "timeout": 10,
        "verbose": False
    }
    def __init__(self, url: str, settings: Dict[str, Any] = None):
        self.settings = settings or CurlCffiRequest.settings
        self.url = url
        self.curl = curl_cffi.Curl()
        self.response_buffer = io.BytesIO()
        self._apply_settings()
        pass

    def _apply_settings(self):
        headers = [header.encode('utf-8') for header in Headers.CURL_CFFI.value]
        self.curl.setopt(curl_cffi.CurlOpt.URL, self.url)
        self.curl.setopt(curl_cffi.CurlOpt.USERAGENT, UserAgents.CURL_CFFI.value)
        self.curl.setopt(curl_cffi.CurlOpt.FOLLOWLOCATION, True)
        self.curl.setopt(curl_cffi.CurlOpt.ACCEPT_ENCODING, 'gzip, deflate')
        self.curl.setopt(curl_cffi.CurlOpt.TIMEOUT, self.settings["timeout"])
        self.curl.setopt(curl_cffi.CurlOpt.VERBOSE, self.settings["verbose"])
        self.curl.setopt(curl_cffi.CurlOpt.HTTPHEADER, headers)
        self.curl.setopt(curl_cffi.CurlOpt.WRITEDATA, self.response_buffer)

    def make_request(self, content_obj: SiteContent) -> SiteContent:
        self.curl.perform()
        content_obj.content = self.response_buffer.getvalue()
        self.response_buffer.flush()
        self.curl.close()
        return content_obj
