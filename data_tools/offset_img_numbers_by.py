import sys
import os
import shutil

if len(sys.argv) < 4 or sys.argv[1] == "-h": print("<path> <offset_by> <new_name>")
offset = int(sys.argv[1])
path = sys.argv[2]
new_name = sys.argv[3]
print(offset)
cwd = os.getcwd()
count = 1

def copy_image(i,offset,count):
    if (i>=0-offset and offset<0) or (i>1-offset and offset>0) or (offset == 0):
        path_to_img = os.path.join(cwd,"batches",path,"s-"+str(i-offset)+".png")
        path_to_new_img = os.path.join(cwd,"batches",new_name,"s-"+str(i)+".png")
        print(path_to_new_img)
        with open(str(path_to_new_img), "w+") as to: 
                shutil.copyfile(str(path_to_img), str(path_to_new_img))  
        count += 1
    return count

for i in range(1,8000):
    count = copy_image(i,offset,count)
    




