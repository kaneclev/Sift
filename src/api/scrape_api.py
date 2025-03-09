from typing import List

from IR.ir_base import IntermediateRepresentation
from scraping.ir_translator import IRTranslator, TargetHandler
from scraping.scraper import ScrapeMethods, Scraper
from scraping.sift_requests.content import SiteContent


class ScrapeDelegator:
    def __init__(self, ir_obj: IntermediateRepresentation):
        self.translator = IRTranslator(ir=ir_obj)
        self.targs: List[TargetHandler] = self.translator.targ_handlers
        self.scrapers = self._construct_scrapers()
        pass

    def scrape(self, alias: str = "", methods: List[ScrapeMethods] = None) -> List[SiteContent]:
        methods = methods or []
        aggregated_results = []
        for scraper in self.scrapers:
            if alias:
                if alias == scraper.targ_handler.alias:
                    scraper.get(methods=methods)
            else:
                scraper.get(methods=methods)
            aggregated_results.extend(scraper.get_discovered(methods=methods))
        return aggregated_results

    def _construct_scrapers(self) -> List[Scraper]:
        scrapers: List[Scraper] = []
        for targ in self.targs:
            scrapers.append(Scraper(targ))
        return scrapers


