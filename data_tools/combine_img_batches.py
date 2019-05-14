import sys
import os
import shutil
count = 1
cwd = os.getcwd()
for i in range(0,len(sys.argv)-1):
    path = sys.argv[i+1]
    for j in range(1,8000):
        try:
            path_to_img = os.path.join(cwd,path,"s-"+j+".png")
            path_to_new_img = os.path.join(cwd,"combined_batches","s-"+j+".png")
            with open(path_to_new_img, "w+") as to: 
                shutil.copyfile(path_to_img, path_to_new_img)  
        except:
            print("Nothing here.")
            break
