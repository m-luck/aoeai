import csv
import sys

path = sys.argv[1]
batch_name = sys.argv[2]
with open(str(path)) as f:
    out_name = 'image_x_y_selectedID_{b}.csv'.format(b=batch_name) 
    with open(out_name, newline="\n", mode='w+') as out: 
        wrtr = csv.writer(out, delimiter=',') 
        for n, line in enumerate(f):
            time, i, data = line.split(':')
            x, y, selected = data.split(',')
            x = int(x)
            y = int(y)
            selected = selected[:-1]
            image_path = '{batch}/s-{np1}.png'.format(batch=str(batch_name), np1=n+2)
            wrtr.writerow([image_path,x,y,selected])
        