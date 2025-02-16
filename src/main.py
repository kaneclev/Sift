from prep import prep  # noqa: F401, I001
from file_operations.sift_file import SiftFile  # noqa: F401
from scraping.sift_requests.request_engine import TargetRequest, BrowserRequest


def main():
    # OS Pathing prep

    browser_req = BrowserRequest("https://www.reddit.com/r/webscraping/comments/1c4jd72/where_to_begin_web_scraping/", "example2")
    html = browser_req.make_request()
    print(html)
    browser_req.quit()
    # When finished, quit the driver to close the browser.

if __name__ == "__main__":
    main()
