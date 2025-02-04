from file_operations.sift_file import SiftFile

testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample2_long.sift"
rep = SiftFile(testfile)
print(rep.show_tree())
