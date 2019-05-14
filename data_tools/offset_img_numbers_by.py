import sys

if sys.argv[1] == None or sys.argv[1] == "-h": print("<path> <offset_by> <new_name>")
offset = int(sys.argv[1])
new_name = sys.argv[3]
print(offset)
cwd = os.getcwd()
count = 1

def copy_image(i,offset,count):
    if (i>=0-offset and offset<0) or (i>1-offset and offset>0) or (offset == 0):
        path_to_img = os.path.join(cwd,path,"s-"+j+".png")
        path_to_new_img = os.path.join(cwd,"combined_batches","s-"+str(i+offset)+".png")
        with open(path_to_new_img, "w+") as to: 
            shutil.copyfile(path_to_img, path_to_new_img)  
        count += 1
    return count

for i in range(1,8000):
    count = copy_image(i,offset,count)
    




