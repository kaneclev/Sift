from file_operations.sift_file import SiftFile
from language.structs.script_tree import ScriptTree

testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample1_long.sift"
rep = SiftFile(testfile)
tree = rep.get_tree()
st = ScriptTree.generate_script_tree(tree)
print(st)
