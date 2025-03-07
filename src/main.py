from prep import prep  # noqa: F401, I001
from api.script_processor import ScriptProcessor  # noqa: F401


def main():
    proc = ScriptProcessor(
        sift_file="../siftscripts/sample1_long.sift")
    ir = proc.to_ir()
    for inst in ir:
        print(f'Instruction: {inst}')
    #print(ir)
if __name__ == "__main__":
    main()
