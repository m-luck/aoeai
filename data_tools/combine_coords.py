import sys
with open("COMBINED_DATA.csv", "w+") as to:
    count = 1
    for i in range(0,len(sys.argv)-1):
        with open(sys.argv[i+1],"r") as f: 
            for line in f:
                time, j, data = line.split(':')
                x,y,selected = data.split(',')
                batch = str(sys.argv[i+1].split('_')[0])
                to.write("{batch}:{time}:{j}:{x},{y},{selected}".format(time=time, j=j, x=x, y=y, selected=selected, batch=batch))
                count += 1