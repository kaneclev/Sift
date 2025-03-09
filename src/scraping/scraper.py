from enum import Enum
from typing import Dict, List

from scraping.sift_requests.content import SiteContent
from scraping.sift_requests.curl_cffi_getter import CurlCffiRequest
from scraping.sift_requests.target_handler import TargetHandler


class ScrapeMethods(Enum):
    CURL_CFFI = "curl_cffi"

class Scraper:
    def __init__(self, target_handler: TargetHandler):
        self.targ_handler = target_handler
        self.content_collected: Dict[ScrapeMethods, List[SiteContent]] = {
            ScrapeMethods.CURL_CFFI: []
        }
        pass

    def get(self, new_url: str = "", methods: List[ScrapeMethods] = None) -> Dict[ScrapeMethods, SiteContent]:
        if not methods:
            methods = [ScrapeMethods.CURL_CFFI]
        url = new_url or self.targ_handler.url
        getter = None
        for method in methods:
            match method:
                case ScrapeMethods.CURL_CFFI:
                    getter = CurlCffiRequest(url=url)
                    content = getter.make_request(content_obj=SiteContent(url=url, alias=self.targ_handler.alias))
                    self.content_collected[ScrapeMethods.CURL_CFFI].append(content)

        return self.content_collected

    def get_discovered(self, methods: List[ScrapeMethods] = None) -> List[SiteContent]:
        discovered: List[SiteContent] = []
        for method, discovered_content in self.content_collected.items():
            if methods:
                if method in methods:
                    discovered.append(discovered_content)
            else:
                discovered.append(discovered_content)
        return discovered_content
