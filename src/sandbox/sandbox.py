from Language.SiftFile import SiftFile
from Language.Structs.ScriptTree import ScriptTree
import re

testfile = "C:/Users/Kane/projects/Sift/siftscripts/lengthy_sample.sift"
rep = SiftFile(testfile)
tree = rep.get_tree()
ScriptTree.generate_script_tree(tree)
