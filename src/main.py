from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401


def main():
    proc = ScriptProcessor(sift_file="C:/Users/Kane/projects/Sift/siftscripts/sample2_long.sift", show_ast=True)
    proc.to_queue()
if __name__ == "__main__":
    main()
