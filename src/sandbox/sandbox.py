from file_operations.script_representations import SiftFile

testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample2_long.sift"
rep = SiftFile(testfile)
rep.parse_file()
print(rep.show_tree())
