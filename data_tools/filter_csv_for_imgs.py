import sys
import csv
import os

cwd= os.getcwd()

correct = {}
directory = os.path.join(cwd,sys.argv[1])
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".jpg"): 
        batch = filename.split('_')[1]
        img_num = filename.split('-')[1].split('.')[0]
        key = batch+"-"+img_num
        correct[key] = True
        if batch =="b6":
            print(key)

with open(sys.argv[2], 'r') as r, open("FIXED_SCOUT.csv",newline="\n",mode="w+") as w:
    wrtr = csv.writer(w, delimiter=',') 
    for i, line in enumerate(r):
        example_img_path, x, y, selected = line.split(',')
        batch, file_name = example_img_path.split('/')[1:3]
        after_s = file_name.split('-')[1]
        number = after_s.split('.')[0]
        key = batch+"-"+number
        if key in correct:
            wrtr.writerow([example_img_path,x,y,int(selected)])