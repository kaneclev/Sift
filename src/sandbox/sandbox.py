from file_operations.sift_file import SiftFile

testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample1_long.sift"
rep = SiftFile(testfile)
print(rep.show_tree())
