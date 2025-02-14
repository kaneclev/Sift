from prep import prep  # noqa: F401, I001
from file_operations.sift_file import SiftFile  # noqa: F401
from scraping.sift_requests.request_engine import TargetRequest


def main():
    # OS Pathing prep

    test = TargetRequest("https://curl-cffi.readthedocs.io/en/latest/cookies.html", targ_name="curl_docs_test")
    response = test.make_request()

if __name__ == "__main__":
    main()
