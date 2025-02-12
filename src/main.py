import time

from file_operations.sift_file import SiftFile
from scraping.make_request import MakeTargetRequest
from prep import prep


def main():
    # OS Pathing prep
    prep()

    testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample2_long.sift"
    start_time = time.perf_counter()
    rep = SiftFile(testfile)
    rep.parse_file()
    json_content = rep.sift_script_to_json()
    MakeTargetRequest(json_content)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")

if __name__ == "__main__":
    main()
