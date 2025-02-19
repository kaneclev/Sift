from prep import prep  # noqa: F401, I001
from file_operations.sift_file import SiftFile  # noqa: F401


def main():
    # OS Pathing prep
    import os
    print(os.getcwd())
    test = SiftFile(file_path=r"C:\Users\Kane\projects\Sift\siftscripts\sample2_long.sift")
    test.parse_file()
    # When finished, quit the driver to close the browser.
    print(test.get_tree_obj())

if __name__ == "__main__":
    main()
