from Language.SiftFile import SiftFile
from Language.Structs.ScriptTree import ScriptTree

testfile = "C:/Users/Kane/projects/Sift/siftscripts/lengthy_sample.sift"
rep = SiftFile(testfile)
tree = rep.get_tree()
st = ScriptTree.generate_script_tree(tree)
for block in st.action_blocks:
    for action in block.actions:
        filt = action.filter_
        print(filt)