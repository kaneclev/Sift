from file_operations.sift_file import SiftFile
from prep import prep
# ! os pathing prep
prep()


testfile = "C:/Users/Kane/projects/Sift/siftscripts/sample2_long.sift"
rep = SiftFile(testfile)
rep.parse_file()
print(rep.show_tree())
