import sys

if sys.argv[1] == None or sys.argv[1] == "-h": print("<path> <offset_by> <new_name>")
offset = int(sys.argv[1])
new_name = sys.argv[3]
old_selected = "Erase this."
print(offset)
with open(sys.argv[2],"r") as f: # File path
    with open(new_name,"w+") as to: 
        count = 1 
        for i, line in enumerate(f):
            time, j, data = line.split(':')
            x,y,selected = data.split(',')
            if i>=0-offset and offset<0: 
                to.write("{time}:{j}:{x},{y},{selected}".format(time=old_time, j=count, x=old_x, y=old_y, selected=selected))
                count += 1
            elif i>1-offset and offset>0: 
                to.write("{time}:{j}:{x},{y},{selected}".format(time=time, j=count, x=x, y=y, selected=old_selected))
                count += 1
            elif offset == 0:
                to.write("{time}:{j}:{x},{y},{selected}".format(time=time, j=count, x=x, y=y, selected=selected))
                count += 1
            old_x, old_y, old_j, old_selected, old_time = x, y, j, selected, time
    




