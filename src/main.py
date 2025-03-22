import argparse
import time

import pika

from api.ipc_management.ipc_options import (  # noqa: F401
    ComTypes,
    IPCOptions,
    MsgType,
    Recievers,
)
from api.script_processor import ScriptProcessor  # noqa: F401
from file_operations.script_representations import RepresentationType, get_script_object
from prep import prep  # noqa: F401, I001

OPTS = {}
def parse_and_communicate():
    # TODO: This should be able to handle other types other than just a file type in the future.
    raw_script = None
    rep = None
    if OPTS["comtype"] == "file":
        raw_script = OPTS["filename"]
        rep = RepresentationType.FILE
    else:
        # TODO the other case is for when we implement new ways of comming with this script
        return []
    script_object = get_script_object(raw=raw_script, rtype=rep)
    processor = ScriptProcessor(script=script_object)
    ast, ir = processor.parse()
    print(f"ast: {ast}, ir: {ir}")
    sent_items = processor.send_ir(ir=ir)
    return sent_items


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
    t = time.time()
    parser = argparse.ArgumentParser(description="Sift CLI Entrypoint")
    valid_args = arg_handler(parser)
    if not valid_args:
        return
    sent_items = parse_and_communicate()

    t1 = time.time()

    print(f"Execution time: {t1 - t} seconds")

if __name__ == "__main__":
    main()
