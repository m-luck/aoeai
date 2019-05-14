import csv
import sys

path = sys.argv[1]
SCOUT = [242859360]
with open(str(path)) as f:
    out_name = 'SCOUT.CSV' 
    with open(out_name, newline="\n", mode='w+') as out: 
        wrtr = csv.writer(out, delimiter=',') 
        for n, line in enumerate(f):
            if n > 0:
                batch,time, i, data = line.split(':')
                x, y, selected = data.split(',')
                if int(selected) in SCOUT:
                    x = int(x)
                    y = int(y)
                    selected = selected[:-1]
                    image_path = 'batches/{batch}/s-{i}.png'.format(batch=batch,i=i)
                    wrtr.writerow([image_path,x,y,selected])
        