from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401
from api.scrape_api import ScrapeDelegator
import time

def main():
    t = time.time()
    proc = ScriptProcessor(
        sift_file="../siftscripts/sample1_long.sift")
    proc.to_ir()
    t1 = time.time()
    print(f"Execution time: {t1 - t} seconds")

if __name__ == "__main__":
    main()
