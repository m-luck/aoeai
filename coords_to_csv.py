import csv

path = sys.argv[1]
batch_name = sys.argv[2]
with open(str(path)) as f:
    with open('image_x_y_selectedID.csv', mode='w+') as out: 
        for n, line in enumerate(f):
            time, i, data = line.split(':')
            x, y, selected = data.split(',')
            x = int(x)
            y = int(y)
            wrtr = csv.writer(out, delimiter=',') 
            image_path = '{batch}/s-{np1}.png'.format(batch=str(batch_name), np1=n+1)
            wrtr.writerow([image_path,x,y,selected])
        