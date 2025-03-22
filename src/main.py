import argparse
from prep import prep  # noqa: F401, I001
from api.parsing_api.coordinator import Coordinator
OPTS = {}

def start_queue_communication(fname: str):
    if not isinstance(fname, list):
        fname = [fname]
    generated = Coordinator.coordinate_parsing(fname)
    print(generated)
def arg_handler(parser: argparse.ArgumentParser) -> bool:
    parser.add_argument("--comtype", choices=["file", "queue"], required=True)
    parser.add_argument("--filename", "-f", required=False)
    args = parser.parse_args()
    for arg in vars(args):
        OPTS[arg] = getattr(args, arg)
    if OPTS["comtype"] == "file":
        if not OPTS["filename"]:
            print("If the communication type is via 'file', then there must be a provided file name through args: [ --filename | -f <filepath>]")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Sift CLI Entrypoint")
    valid_args = arg_handler(parser)
    if not valid_args:
        return
    if OPTS["comtype"] == "file":
        start_queue_communication(OPTS["filename"])



if __name__ == "__main__":
    main()
