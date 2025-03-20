import os
from typing import Dict
from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401
from api.ipc_management.ipc_options import IPCOptions, MsgType, Recievers, ComTypes  # noqa: F401
import time
import argparse
OPTS = {}
def parse_and_communicate():
    ast_opts = {
        "save": OPTS["debug_save"] or False,
        "show": OPTS["debug"] or False
    }
    json_opts = {
        "save": OPTS["debug_save"] or False,
        "show": OPTS["debug"] or False
    }
    pickle_opts = {
        "save": OPTS["pickle"] or False,
        "show": OPTS["debug"] or False
    }

    processor = ScriptProcessor(
        sift_file=OPTS["file"], 
        ast=ast_opts, 
        json=json_opts, 
        pickle=pickle_opts)

    processor.generate_ast()
    processor.to_ir()
    sent_items = processor.send_ir()
    return sent_items

def start_scrape(items_sent: list):
    os.system("make build")

    for item in items_sent:
        for k, v in item.items():
            if k == MsgType.JSON:
                pattern = OPTS["pattern"]
                if pattern:
                    os.system(f"./bin/siftrequests -finput {pattern} --match-type {OPTS['match_type']}")
                else:
                    os.system(f"./bin/siftrequests -finput {os.path.basename(v)} --match-type {OPTS['match_type']}")

def arg_handler(parser: argparse.ArgumentParser) -> Dict[str, str]:
    parser.add_argument("-f", "--file", help="File to parse", type=str, required=True)
    parser.add_argument("-d", "--debug", help="Show intermediate steps in the parsing process.", action="store_true", required=False)
    parser.add_argument("-ds", "--debug-save", help="Save intermediate steps in the parsing process.", action="store_true", required=False)
    parser.add_argument("-pkl", "--pickle", help="Save the IR as a pickle file.", action="store_true", required=False)
    parser.add_argument("-mt", "--match-type", choices=["loose", "strict"], default="strict", help="Tells the Go consumer to either match strictly the file we are parsing now, or to make requests for all previous files who fit a common pattern (loose)")
    parser.add_argument("-p", "--pattern", help="Pattern to match files against", type=str, required=False)

    args = parser.parse_args()
    for arg in vars(args):
        OPTS[arg] = getattr(args, arg)
    return OPTS

def main():
    t = time.time()
    parser = argparse.ArgumentParser(description="Sift CLI Entrypoint")
    arg_handler(parser)
    sent_items = parse_and_communicate()
    if sent_items:
        start_scrape(sent_items)
    else:
        raise ValueError("Nothing was sent to the scraper. Exiting.")

    t1 = time.time()

    print(f"Execution time: {t1 - t} seconds")

if __name__ == "__main__":
    main()
