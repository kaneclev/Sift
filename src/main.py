from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401
from api.ipc_management.ipc_options import IPCOptions, MsgType, Recievers, ComTypes
import time
def main():
    t = time.time()
    opts = {
        'save': True,
        'show': True
    }
    ScriptProcessor(
        sift_file="siftscripts/targets_only.sift", pickle=opts, ast=opts, json=opts)

    t1 = time.time()

    print(f"Execution time: {t1 - t} seconds")

if __name__ == "__main__":
    main()
