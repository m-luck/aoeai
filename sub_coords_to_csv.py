import csv
import sys

# SCOUT_B3 = 396565680
# SCOUT_B3 = 242859360

path = sys.argv[1]
batch_name = sys.argv[2]
with open(str(path)) as f:
    out_name = 'image_x_y_selectedID_{b}.csv'.format(b=batch_name) 
    with open(out_name, newline="\n", mode='w+') as out: 
        wrtr = csv.writer(out, delimiter=',') 
        for n, line in enumerate(f):
            if n > 0:
                time, i, data = line.split(':')
                x, y, selected = data.split(',')
                if int(selected) == SCOUT_B3:
                    x = int(x)
                    y = int(y)
                    selected = selected[:-1]
                    image_path = '{batch}/s-{np1}.png'.format(batch=str(batch_name), np1=n+1)
                    wrtr.writerow([image_path,x,y,selected])
        