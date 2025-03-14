from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401
from scraping.ir_translator import IRTranslator
import time
def main():
    t = time.time()
    spro = ScriptProcessor(
        sift_file="../siftscripts/sample1_long.sift", show_pickle=True)
    translation = IRTranslator(spro.ir_obj)
    for a in translation.targ_handlers:
        print(a.to_dict())
    t1 = time.time()

    print(f"Execution time: {t1 - t} seconds")

if __name__ == "__main__":
    main()
